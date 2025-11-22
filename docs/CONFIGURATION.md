# Configuration Guide

Complete guide to configuring your Leipzig Transport Display.

## Quick Start

### Method 1: Edit main.py (Simple)

Find the configuration section (lines 19-50) and edit:

```python
# Station IDs
BUS_STATION_ID = "NNNNNN"     # Your bus station
TRAM_STATION_ID = "NNNNNN"    # Your tram station

# Filters
BUS_FILTER = {
    "Bus NN": ["End station name"]
}

TRAM_FILTER = {
    "STR NN": ["End station name"],
    "STR NN": ["End station name"]
}
```

### Method 2: Create config_local.py (Recommended)

**Advantages:**
- Keep personal settings separate from code
- Won't be committed to Git (in .gitignore)
- Easy to update code without losing your config

# Copy example config

# Edit your settings

The program automatically loads `config_local.py` if it exists.

---

## Finding Your Station IDs

### Step 1: Search for your station

```bash
# Replace "Hauptbahnhof Leipzig" with your station name
curl "https://v6.db.transport.rest/locations?query=Hauptbahnhof%20Leipzig"
```

**Response:**
```json
[
  {
    "type": "stop",
    "id": "008010205",           ← THIS IS YOUR STATION ID
    "name": "Leipzig Hauptbahnhof",
    "location": {...},
    ...
  }
]
```

### Step 2: Test departures from that station

```bash
# Replace with your station ID
curl "https://v6.db.transport.rest/stops/008010205/departures?duration=120"
```

**Response shows:**
```json
{
  "departures": [
    {
      "line": {
        "name": "STR 1"       ← LINE NAME
      },
      "direction": "Lausen",  ← DIRECTION
      "when": "2024-11-22T15:30:00+01:00"
    },
    ...
  ]
}
```

### Step 3: Add to your config

Use the **line name** and **direction** from the response:

```python
TRAM_FILTER = {
    "STR 1": ["Lausen"]   ← FROM API RESPONSE
}
```

---

## Filtering Lines and Directions

### Show specific lines only

```python
# Show only Bus 60 and STR 15
BUS_FILTER = {
    "Bus NN": ["End station name"]
}

TRAM_FILTER = {
    "STR NN": ["End station name"]
}
```

### Show multiple directions of the same line

```python
# STR 15 going BOTH directions
TRAM_FILTER = {
    "STR 15": ["Meusdorf", "Angerbrücke"]
}
```

### Show multiple lines

```python
TRAM_FILTER = {
    "STR 15": ["Meusdorf"],
    "STR 8": ["Sellerhausen"],
    "STR 11": ["Schkeuditz"],
    "STR N2": ["Hauptbahnhof"]  # Night tram
}
```

### Show ALL departures (no filter)

```python
# Show everything!
BUS_FILTER = None
TRAM_FILTER = None
```

**Or use empty dict:**
```python
BUS_FILTER = {}
TRAM_FILTER = {}
```

---

## 🎨 Customizing Colors

### Line Colors

Each line can have its own color (RGB tuple):

```python
LINE_COLORS = {
    "Bus 60": (128, 0, 128),   # Purple
    "STR 8": (255, 255, 0),    # Yellow
    "STR 15": (0, 100, 255),   # Blue
}
```

**RGB Format:** `(Red, Green, Blue)` - each value 0-255

### Common Colors

```python
# Basic
(255, 0, 0)       # Red
(0, 255, 0)       # Green
(0, 0, 255)       # Blue
(255, 255, 0)     # Yellow
(255, 255, 255)   # White

# Advanced
(255, 128, 0)     # Orange
(128, 0, 128)     # Purple
(0, 255, 255)     # Cyan
(255, 0, 255)     # Magenta
(128, 128, 128)   # Gray

# Dimmed (for night)
(64, 0, 0)        # Dark Red
(0, 64, 0)        # Dark Green
(64, 64, 0)       # Dark Yellow
```

### Time Colors

```python
COLOR_NOW = (255, 0, 0)        # Red for "now" (departing!)
COLOR_TIME = (255, 255, 255)   # White for regular times
```

### Dynamic colors by urgency

Add this function to `main.py`:

```python
def get_color_by_urgency(minutes):
    """Color based on departure time"""
    if minutes is None:
        return (128, 128, 128)  # Gray - N/A
    elif minutes == 0:
        return (255, 0, 0)      # Red - NOW!
    elif minutes <= 2:
        return (255, 128, 0)    # Orange - SOON!
    elif minutes <= 5:
        return (255, 255, 0)    # Yellow - coming
    else:
        return (0, 255, 0)      # Green - plenty of time

# Use in format_departure_colored():
time_color = get_color_by_urgency(minutes)
```

---

## Display Settings

### Brightness

```python
lcd = LEDMatrixDisplay(
    rows=32,
    cols=64,
    brightness=50  # 0-100, adjust for your room
)
```

### Auto-brightness by time

```python
from datetime import datetime

hour = datetime.now().hour

if 6 <= hour < 22:
    brightness = 50  # Day
else:
    brightness = 20  # Night

lcd = LEDMatrixDisplay(brightness=brightness)
```

---

## Update Intervals

### Display update (countdown)

```python
DISPLAY_UPDATE_INTERVAL = 20  # seconds
```

How often the countdown refreshes (5m → 4m → 3m...).

**Recommendations:**
- **Smooth countdown:** 15-20 seconds
- **Battery saving:** 30-60 seconds

### API requests

```python
API_UPDATE_INTERVAL = 60  # seconds
```

How often to fetch new data from the API.

**Recommendations:**
- **Normal:** 60 seconds (every minute)
- **High traffic:** 30 seconds
- **Low traffic:** 120 seconds (every 2 minutes)

**Don't set too low!** Respect the API (no API key required = be reasonable).

---

## Using Different Cities

This project uses Deutsche Bahn's HAFAS API which covers all German cities!

### Examples

**Berlin:**
```python
BUS_STATION_ID = "900100001"  # Berlin Hauptbahnhof
TRAM_FILTER = {
    "M10": ["Warschauer Str."],
    "M5": ["Hohenschönhausen"]
}
```

**Munich:**
```python
TRAM_STATION_ID = "008000261"  # München Hauptbahnhof
TRAM_FILTER = {
    "STR 19": ["Pasing"],
    "STR 16": ["Romanplatz"]
}
```

**Hamburg:**
```python
BUS_STATION_ID = "008002549"  # Hamburg Hauptbahnhof
BUS_FILTER = {
    "Bus 3": ["Rathausmarkt"],
    "Bus 31": ["Altona"]
}
```

**Find stations:** https://v6.db.transport.rest/locations?query=YOUR_CITY

---

## Full Configuration Example

```python
# config_local.py

# === STATION IDS ===
BUS_STATION_ID = "130637"     # Lindenauer Hafen
TRAM_STATION_ID = "958956"    # Saarländer Str.

# === FILTERS ===
BUS_FILTER = {
    "Bus 60": ["Lipsiusstraße"]
}

TRAM_FILTER = {
    "STR 15": ["Meusdorf", "Angerbrücke"],  # Both directions
    "STR 8": ["Sellerhausen"],
    "STR N2": ["Hauptbahnhof"]              # Night line
}

# === COLORS ===
LINE_COLORS = {
    "Bus 60": (128, 0, 128),   # Purple
    "STR 8": (255, 255, 0),    # Yellow
    "STR 15": (0, 100, 255),   # Blue
    "STR N2": (255, 255, 255)  # White
}

COLOR_NOW = (255, 0, 0)        # Red for "now"
COLOR_TIME = (255, 255, 255)   # White for times

# === DISPLAY ===
# Brightness set in main():
# lcd = LEDMatrixDisplay(brightness=40)

# === UPDATE INTERVALS ===
DISPLAY_UPDATE_INTERVAL = 20   # seconds
API_UPDATE_INTERVAL = 60       # seconds
```

---

## Testing Your Configuration

### 1. Verify station IDs work

```bash
curl "https://v6.db.transport.rest/stops/YOUR_STATION_ID/departures?duration=120"
```

Should return departures, not an error.

### 2. Test filters

```bash
# Run the program
sudo python3 main.py

# Check console output:
[15:30:45] Fetching data from API...
  OK! Bus: Bus 60 at 15:35
  OK! Trams: 3 departures
    - STR 15 at 15:32
    - STR 8 at 15:38
    - STR N2 at 15:45
```

If a line doesn't appear:
- Check the **exact line name** in API response
- Check the **exact direction** name
- Names are case-sensitive!

### 3. Verify colors

Look at the display - do colors match your expectations?

---

## Common Issues

### "No data received"

**Problem:** Station ID wrong or no service at that station.

**Solution:**
```bash
# Verify station exists
curl "https://v6.db.transport.rest/stops/YOUR_ID/departures?duration=120"
```

### Line not showing

**Problem:** Filter doesn't match API response.

**Solution:**
```bash
# Check exact line name and direction
curl "https://v6.db.transport.rest/stops/YOUR_ID/departures?duration=120" | grep -A 5 "line"
```

Use the **exact** name from response:
- `"STR 15"` not `"Tram 15"`
- `"Bus 60"` not `"60"`

### Wrong color

**Problem:** Line name doesn't match `LINE_COLORS` key.

**Solution:** Make sure keys match exactly:
```python
# In API response:
"line": {"name": "STR 15"}

# In your config must be:
LINE_COLORS = {
    "STR 15": (0, 100, 255)  # Exact match!
}
```

### Config not loading

**Problem:** `config_local.py` has syntax error.

**Solution:**
```bash
# Test Python syntax
python3 -c "import config_local"

# Should print nothing if OK
# If error, fix the syntax
```

---

## Advanced Configuration

### Multiple stations

Track departures from different stations for bus vs tram:

```python
BUS_STATION_ID = "130637"      # Station A
TRAM_STATION_ID = "958956"     # Station B (different location)
```

### Night mode

```python
from datetime import datetime

hour = datetime.now().hour

# Dimmer colors at night
if 22 <= hour or hour < 6:
    LINE_COLORS = {
        "Bus 60": (40, 0, 40),    # Dark purple
        "STR 8": (80, 80, 0),     # Dark yellow
        "STR 15": (0, 30, 80)     # Dark blue
    }
else:
    LINE_COLORS = {
        "Bus 60": (128, 0, 128),
        "STR 8": (255, 255, 0),
        "STR 15": (0, 100, 255)
    }
```

### Refresh on schedule

Only fetch during working hours:

```python
# In fetch_api_data():
hour = datetime.now().hour
if hour < 5 or hour > 23:
    print("Outside service hours, skipping API request")
    return
```

---
