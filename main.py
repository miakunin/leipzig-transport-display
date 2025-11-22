#!/usr/bin/env python3
"""
Main application for LED display on Raspberry Pi

Features:
- Display updates every 20 seconds (smooth countdown)
- API requests every 60 seconds (reduce load)
- Local time calculation between API updates
- Automatic retry on API failures
- Multi-color display: line numbers in route colors, "now" in red
"""
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from transport_service import TransportService
from led_matrix_display import LEDMatrixDisplay


# === CONFIGURATION ===
# Copy this section to config_local.py and customize for your location
# See config_example.py for examples

DISPLAY_UPDATE_INTERVAL = 20  # seconds - how often to refresh display
API_UPDATE_INTERVAL = 60      # seconds - how often to fetch new data from API

# Station IDs (find yours at: https://v6.db.transport.rest/locations?query=YourStation)
BUS_STATION_ID = "YOUR_BUS_STATION_ID"        # Replace with your bus station ID 
TRAM_STATION_ID = "YOUR_TRAM_STATION_ID"      # Replace with your tram station ID
                                              # These are the stations you want to monitor

# Filters - only show specific lines and directions
BUS_FILTER = {
    "Bus XX": ["Your Destination"]           # Replace with your bus line
}

TRAM_FILTER = {
    "STR YY": ["Your Destination 1"],        # Replace with your tram lines
    "STR ZZ": ["Your Destination 2"]
}
                                             # these are the route destinations for bus/tram you want to track
                                             # so you may monitor a specific route's direction (e.g. -> Hauptbahnhof)

# Line colors (RGB) - customize for your lines
LINE_COLORS = {
    "Bus XX": (128, 0, 128),   # Purple
    "STR YY": (255, 255, 0),   # Yellow
    "STR ZZ": (0, 100, 255)    # Blue
}

# Time colors
COLOR_NOW = (255, 0, 0)        # Red for "now"
COLOR_TIME = (255, 255, 255)   # White for regular time

# Import local config if exists (optional)
try:
    from config_local import *
    print("OK: Loaded configuration from config_local.py")
except ImportError:
    print("!!! Using default configuration. Create config_local.py for your settings.")
    print("  See config_example.py for examples.")


class DepartureState:
    """
    Class to store and manage departure information
    
    Stores absolute departure times and calculates minutes
    until departure on demand.
    """
    
    def __init__(self):
        self.bus_departure: Optional[Dict] = None
        self.tram_departures: List[Dict] = []
        self.last_update: Optional[datetime] = None
    
    def update_bus(self, departure: Optional[Dict]):
        """Update bus departure data"""
        self.bus_departure = departure
        self.last_update = datetime.now()
    
    def update_trams(self, departures: List[Dict]):
        """Update tram departures data"""
        self.tram_departures = departures[:3]  # Keep max 3
        self.last_update = datetime.now()
    
    def get_bus_minutes(self) -> Optional[int]:
        """Calculate minutes until bus departure"""
        if not self.bus_departure:
            return None
        
        # Check if data is too old (>4 minutes = 240 seconds)
        if self.last_update:
            cache_age = (datetime.now() - self.last_update).total_seconds()
            if cache_age > 240:
                return None  # Data too old, show N/A
        
        now = datetime.now().astimezone()
        dep_time = self.bus_departure['departure_time']
        
        delta = dep_time - now
        minutes = int(delta.total_seconds() / 60)
        
        return max(0, minutes)  # Never negative
    
    def get_tram_minutes(self, index: int) -> Optional[int]:
        """Calculate minutes until tram departure at given index"""
        if index >= len(self.tram_departures):
            return None
        
        # Check if data is too old (>4 minutes = 240 seconds)
        if self.last_update:
            cache_age = (datetime.now() - self.last_update).total_seconds()
            if cache_age > 240:
                return None  # Data too old, show N/A
        
        now = datetime.now().astimezone()
        dep_time = self.tram_departures[index]['departure_time']
        
        delta = dep_time - now
        minutes = int(delta.total_seconds() / 60)
        
        return max(0, minutes)
    
    def is_stale(self, max_age_seconds: int = 300) -> bool:
        """Check if data is too old (default: 5 minutes)"""
        if not self.last_update:
            return True
        
        age = (datetime.now() - self.last_update).total_seconds()
        return age > max_age_seconds


def format_departure_colored(line: str, minutes: Optional[int], delay: int = 0) -> Dict:
    """
    Format departure for LED matrix with color segments
    
    Args:
        line: Line name (e.g., "Bus 60", "STR 15")
        minutes: Minutes until departure (None if no data)
        delay: Delay in minutes
        
    Returns:
        Dictionary with colored segments
    """
    # Get line color (default white if not in config)
    line_color = LINE_COLORS.get(line, (255, 255, 255))
    
    # Shorten line name
    if line.startswith("Bus "):
        short_line = line.replace(" ", "")  # "Bus60"
    elif line.startswith("STR "):
        short_line = "STR" + line[4:]  # "STR15" or "STR8"
    else:
        short_line = line[:5]
    
    short_line = short_line.ljust(5)  # Pad to 5 chars
    
    # Format time
    if minutes is None:
        time_str = "N/A"
        time_color = (128, 128, 128)  # Grey for N/A
    elif minutes == 0:
        time_str = " now"
        time_color = COLOR_NOW  # RED for "now"!
    elif minutes < 60:
        time_str = f"{minutes:3d}m"
        time_color = COLOR_TIME
    else:
        time_str = f"{minutes//60:2d}h"
        time_color = COLOR_TIME
    
    # Add delay if present
    if delay > 0 and minutes is not None:
        time_str = f"{time_str}+{delay}"
        time_str = time_str.rjust(5)
    
    # Build colored segments
    return {
        "text": f"{short_line}{time_str}",
        "segments": [
            {"text": short_line, "color": line_color},  # Line number in route color
            {"text": time_str, "color": time_color}      # Time in appropriate color
        ]
    }


def fetch_api_data(service: TransportService, state: DepartureState):
    """
    Fetch fresh data from API and update state
    
    Args:
        service: TransportService instance
        state: DepartureState to update
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching data from API...")
    
    # Fetch bus
    try:
        bus_deps = service.get_departures(BUS_STATION_ID, BUS_FILTER, max_trips=1)
        if bus_deps:
            state.update_bus(bus_deps[0])
            print(f"  OK! Bus: {bus_deps[0]['line']} at {bus_deps[0]['departure_time'].strftime('%H:%M')}")
        else:
            print("  -X- Bus: no data")
    except Exception as e:
        print(f"  -X- Bus error: {e}")
    
    # Fetch trams
    try:
        tram_deps = service.get_departures(TRAM_STATION_ID, TRAM_FILTER, max_trips=3)
        if tram_deps:
            state.update_trams(tram_deps)
            print(f"  OK! Trams: {len(tram_deps)} departures")
            for dep in tram_deps:
                print(f"    - {dep['line']} at {dep['departure_time'].strftime('%H:%M')}")
        else:
            print("  -X- Trams: no data")
    except Exception as e:
        print(f"  -X- Trams error: {e}")


def update_display(lcd: LEDMatrixDisplay, state: DepartureState):
    """
    Update display with current state and multi-color rendering
    
    Colors:
    - Line numbers: route-specific colors (defined in LINE_COLORS)
    - "now": RED
    - Times: white
    
    Args:
        lcd: LEDMatrixDisplay instance
        state: Current departure state
    """
    lines = []
    
    # Line 1: Bus
    bus_minutes = state.get_bus_minutes()
    if state.bus_departure:
        delay = state.bus_departure.get('delay', 0)
        line = state.bus_departure['line']
        lines.append(format_departure_colored(line, bus_minutes, delay))
    else:
        # No data - grey text
        lines.append({
            "segments": [
                {"text": "Bus  ", "color": (128, 0, 128)},
                {"text": " N/A", "color": (128, 128, 128)}
            ]
        })
    
    # Lines 2-4: Trams
    for i in range(3):
        tram_minutes = state.get_tram_minutes(i)
        
        if i < len(state.tram_departures):
            dep = state.tram_departures[i]
            delay = dep.get('delay', 0)
            line = dep['line']
            lines.append(format_departure_colored(line, tram_minutes, delay))
        else:
            lines.append("")  # Empty line
    
    # Display with colors!
    lcd.write_lines(lines)
    
    # Print to console
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] Display updated:")
    for i, line in enumerate(lines):
        if line:
            if isinstance(line, dict):
                text = line.get('text', '?')
                print(f"  Line {i+1}: {text}")
            else:
                print(f"  Line {i+1}: {line}")


def main():
    """Main application loop"""
    
    print("=" * 50)
    print("Leipzig Transport Display - Multi-Color Version")
    print("=" * 50)
    print(f"Display updates: every {DISPLAY_UPDATE_INTERVAL}s")
    print(f"API updates: every {API_UPDATE_INTERVAL}s")
    print("=" * 50)
    
    # Initialize components
    service = TransportService(max_retries=3, retry_delay=2.0)
    state = DepartureState()
    
    lcd = LEDMatrixDisplay(
        rows=32,
        cols=64,
        brightness=50
    )
    
    # Initial fetch - retry until we get data!
    print("\nInitial data fetch (will retry until success)...")
    while not state.bus_departure and not state.tram_departures:
        fetch_api_data(service, state)
        
        if not state.bus_departure and not state.tram_departures:
            print("No data received, retrying in 10 seconds...")
            time.sleep(10)
    
    print("\nOK! Initial data received!")
    print("\nStarting update loop...\n")
    
    # Timing variables
    last_api_update = time.time()
    last_display_update = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            # === API UPDATE (every 60 seconds) ===
            if current_time - last_api_update >= API_UPDATE_INTERVAL:
                fetch_api_data(service, state)
                last_api_update = current_time
            
            # === DISPLAY UPDATE (every 20 seconds) ===
            if current_time - last_display_update >= DISPLAY_UPDATE_INTERVAL:
                update_display(lcd, state)
                last_display_update = current_time
                
                # Warn if data is stale (>4 minutes)
                if state.is_stale(max_age_seconds=240):
                    print("  !! Warning: Data is >4 minutes old, showing N/A")
            
            # Sleep a bit to avoid busy loop
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        lcd.clear()
        lcd.close()
        print("Stopped.")


if __name__ == '__main__':
    main()
