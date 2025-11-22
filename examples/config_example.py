"""
Configuration examples for Leipzig Transport Display

Copy this file to config_local.py and customize for your location.
config_local.py is gitignored, so your personal settings won't be committed.
"""

# === EXAMPLE 1: Leipzig Lindenau (West) ===

# Station IDs
BUS_STATION_ID = "130637"     # Lindenauer Hafen
TRAM_STATION_ID = "958956"    # Saarländer Str.

# Filters
BUS_FILTER = {
    "Bus 60": ["Lipsiusstraße"]
}

TRAM_FILTER = {
    "STR 15": ["Meusdorf", "Angerbrücke"],  # Both directions
    "STR 8": ["Sellerhausen"],
    "STR N2": ["Hauptbahnhof"]              # Night tram
}

# Line colors (RGB) - Leipzig LVB colors
LINE_COLORS = {
    "Bus 60": (128, 0, 128),   # Purple
    "STR 8": (255, 255, 0),    # Yellow
    "STR 15": (0, 100, 255),   # Blue
    "STR N2": (255, 255, 255)  # White for night line
}


# === EXAMPLE 2: Leipzig Hauptbahnhof (Central Station) ===

"""
# Station IDs
BUS_STATION_ID = "008010205"   # Leipzig Hauptbahnhof
TRAM_STATION_ID = "008010205"  # Same station for trams

# Filters
BUS_FILTER = {
    "Bus 89": ["Portitz"],
    "Bus 131": ["Flughafen"]   # Airport bus
}

TRAM_FILTER = {
    "STR 1": ["Lausen"],
    "STR 3": ["Taucha"],
    "STR 16": ["Lößnig"]
}

# Line colors
LINE_COLORS = {
    "Bus 89": (255, 128, 0),   # Orange
    "Bus 131": (255, 0, 0),    # Red (important - airport!)
    "STR 1": (128, 0, 255),    # Purple
    "STR 3": (0, 255, 0),      # Green
    "STR 16": (0, 255, 255)    # Cyan
}
"""


# === EXAMPLE 3: Leipzig Südvorstadt (South) ===

"""
# Station IDs
BUS_STATION_ID = "130638"      # Karl-Liebknecht-Str.
TRAM_STATION_ID = "958960"     # Connewitz, Kreuz

# Filters
TRAM_FILTER = {
    "STR 9": ["Markkleeberg-Ost"],
    "STR 10": ["Lößnig"],
    "STR 11": ["Markkleeberg-West"]
}

# Only trams (no buses)
BUS_FILTER = {}

# Line colors
LINE_COLORS = {
    "STR 9": (255, 255, 0),    # Yellow
    "STR 10": (0, 255, 0),     # Green
    "STR 11": (0, 128, 255)    # Blue
}
"""


# === HOW TO FIND YOUR STATION IDS ===

"""
1. Search for your station:
   curl "https://v6.db.transport.rest/locations?query=Hauptbahnhof%20Leipzig"

2. Look for the 'id' field in the response

3. Test departures:
   curl "https://v6.db.transport.rest/stops/YOUR_STATION_ID/departures?duration=120"

4. Find the line names and directions you want to filter

5. Add to BUS_FILTER or TRAM_FILTER
"""


# === COLOR PALETTE ===

"""
Common RGB colors:

(255, 0, 0)       # Red
(0, 255, 0)       # Green
(0, 0, 255)       # Blue
(255, 255, 0)     # Yellow
(255, 0, 255)     # Magenta
(0, 255, 255)     # Cyan
(255, 255, 255)   # White
(255, 128, 0)     # Orange
(128, 0, 128)     # Purple
(255, 192, 203)   # Pink
(128, 128, 128)   # Gray
(0, 128, 0)       # Dark Green
(0, 0, 128)       # Navy Blue
(128, 0, 0)       # Maroon

For dimmer colors (night mode), divide values by 2-3:
(85, 0, 0)        # Dark Red
(42, 42, 0)       # Dark Yellow
"""


# === ADVANCED OPTIONS ===

# Update intervals
DISPLAY_UPDATE_INTERVAL = 20   # seconds between display refreshes
API_UPDATE_INTERVAL = 60       # seconds between API requests

# Time colors
COLOR_NOW = (255, 0, 0)        # Red for "now" - very visible!
COLOR_TIME = (255, 255, 255)   # White for regular times


# === USAGE ===

"""
1. Copy this file:
   cp config_example.py config_local.py

2. Edit config_local.py with your settings

3. Run the program:
   sudo python3 main.py

The program will automatically load config_local.py if it exists,
otherwise it will use the defaults from main.py
"""
