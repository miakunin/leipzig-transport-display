"""
Module for working with transport API and getting Leipzig schedule

Enhanced version with retry logic and better reliability
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class TransportService:
    """
    Service for getting public transport schedule information
    
    Features:
    - Automatic retry on failures
    - Caching of last successful response
    - Better error handling
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        """
        Initialize REST API client
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.base_url = "https://v6.db.transport.rest"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Cache for last successful responses
        self._cache = {}
        self._cache_time = {}
    
    def _make_request_with_retry(self, url: str, params: dict, cache_key: str = None) -> Optional[dict]:
        """
        Make HTTP request with automatic retry
        
        Args:
            url: Full URL to request
            params: Query parameters
            cache_key: Key for caching (optional)
            
        Returns:
            Parsed JSON response or None
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Make request
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Cache successful response
                    if cache_key:
                        self._cache[cache_key] = data
                        self._cache_time[cache_key] = datetime.now()
                    
                    return data
                else:
                    last_error = f"HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                last_error = "Timeout"
            except requests.exceptions.ConnectionError:
                last_error = "Connection error"
            except Exception as e:
                last_error = str(e)
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                print(f"Request failed ({last_error}), retrying in {self.retry_delay}s... (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
        
        # All retries failed
        print(f"All retry attempts failed: {last_error}")
        
        # Return cached data if available
        if cache_key and cache_key in self._cache:
            cache_age = (datetime.now() - self._cache_time[cache_key]).total_seconds()
            print(f"Using cached data (age: {cache_age:.0f}s)")
            return self._cache[cache_key]
        
        return None
    
    def find_station(self, station_name: str) -> Optional[Dict]:
        """
        Find station by name using the locations endpoint
        
        Args:
            station_name: Station name to search for
            
        Returns:
            Dictionary with station information or None
        """
        url = f"{self.base_url}/locations"
        params = {
            "query": station_name,
            "results": 3
        }
        
        data = self._make_request_with_retry(url, params)
        
        if data and len(data) > 0:
            station = data[0]
            return {
                'id': station.get('id'),
                'name': station.get('name'),
                'latitude': station.get('location', {}).get('latitude'),
                'longitude': station.get('location', {}).get('longitude')
            }
        
        return None
    
    def get_departures(self, station_id: str, filters: dict = None, 
                      max_trips: int = 10) -> List[Dict]:
        """
        Get next departures from a station with optional filtering
        
        Args:
            station_id: Station ID
            filters: Dictionary of line filters
                    Example: {"Bus 60": ["Hauptbahnhof"], "STR 15": ["Miltitz"]}
            max_trips: Maximum number of departures to return
            
        Returns:
            List of departure dictionaries with absolute departure times
        """
        url = f"{self.base_url}/stops/{station_id}/departures"
        params = {"duration": 120}
        cache_key = f"departures_{station_id}"
        
        data = self._make_request_with_retry(url, params, cache_key)
        
        if not data:
            return []
        
        departures = data.get('departures', [])
        result = []
        
        for dep in departures:
            line = dep.get('line', {}).get('name', 'N/A')
            direction = dep.get('direction') or 'Unknown'
            
            # Apply filters if provided
            if filters:
                if line not in filters:
                    continue
                if direction not in filters[line]:
                    continue
            
            # Process departure time
            when = dep.get('when', '')
            if not when:
                continue
            
            # Parse ISO timestamp
            try:
                dep_time = datetime.fromisoformat(when.replace('Z', '+00:00'))
            except:
                continue
            
            # Get delay
            delay = dep.get('delay', 0)
            delay_minutes = delay // 60 if delay else 0
            
            result.append({
                'line': line,
                'direction': direction,
                'departure_time': dep_time,  # Absolute datetime!
                'delay': delay_minutes,
                'platform': dep.get('platform')
            })
            
            if len(result) >= max_trips:
                break
        
        return result
