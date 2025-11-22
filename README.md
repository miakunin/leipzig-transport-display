# Leipzig Public Transport Display

Real-time departure display for Leipzig buses and trams on a **64x32 RGB LED Matrix** powered by Raspberry Pi.

![Display Photo]([images/display_photo.jpg](https://github.com/miakunin/leipzig-transport-display/blob/main/images/display_photo.png))

## Features

- **Multi-color display** - Different colors for each line (Bus 60 purple, STR 8 yellow, STR 15 blue)
- **"now" alert** - Departing vehicles shown in RED
- **Real-time countdown** - Updates every 20 seconds
- **Smart caching** - API requests every 60 seconds, reduces load
- **Stale data handling** - Shows "N/A" if data >4 minutes old
- **Auto-retry** - Robust error handling and automatic reconnection
- **Multiple lines** - Track 1 bus + 3 tram lines simultaneously

## Display Format

```
┌────────────────┐
│ Bus80   5m     │  ← Purple number, white time
│ STR12  now     │  ← Blue number, RED "now"!
│ STR7   12m     │  ← Yellow number, white time
│ STR12  1h      │  ← Blue number (2+ departures of same line)
└────────────────┘
```

## Hardware Requirements

- **Raspberry Pi 3B+** (or newer: 3A+, 4, 5, Zero 2W), can work on ESP32
- **64x32 RGB LED Matrix** (P2.5 or P3, HUB75 interface)
- **Power supplies:**
  - RPi: 5V 2.5A+ (official power supply recommended)
  - LED Matrix: 5V 3-4A+ (separate power supply!)
- **Connecting wires:**
  - For permanent install: **RGB Matrix HAT** with buffers (highly recommended!)
  - For testing: Female-Female Dupont wires (short as possible, <20cm)
  - **Avoid breadboards for final install** - causes flickering!

## Installation

### Quick Start

```bash
# 1. Install rpi-rgb-led-matrix library
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)

# 2. Clone this repository
cd ~
git clone https://github.com/YOUR_USERNAME/leipzig-transport-display.git
cd leipzig-transport-display

# 3. Install Python dependencies
pip3 install -r requirements.txt

# 4. Configure your stations and lines
nano main.py
# Edit BUS_STATION_ID, TRAM_STATION_ID, and filters

# 5. Run!
sudo python3 main.py
```

For detailed instructions, see [INSTALLATION.md](docs/INSTALLATION.md)

## Configuration

Edit `main.py` to customize:

```python
# Station IDs (find yours at https://v6.db.transport.rest/locations?query=YourStation)
BUS_STATION_ID = "NNNNNN"     # Lindenauer Hafen
TRAM_STATION_ID = "NNNNNN"    # Saarländer Str.

# Filter by line and direction
BUS_FILTER = {
    "Bus 80": ["End station name"]
}

TRAM_FILTER = {
    "STR 15": ["End station name 1", "End station name 2"],  # Trams
    "STR 8": ["End station name"],
    "STR N2": ["End station name"]  # Night tram
}

# Colors (RGB tuples)
LINE_COLORS = {
    "Bus 60": (128, 0, 128),   # Purple
    "STR 8": (255, 255, 0),    # Yellow
    "STR 15": (0, 100, 255),   # Blue
    "STR N2": (255, 255, 255)  # White
}

# Display settings
lcd = LEDMatrixDisplay(
    rows=32,
    cols=64,
    brightness=40  # 0-100, adjust for your environment
)
```

See [CONFIGURATION.md](docs/CONFIGURATION.md) for more options.

## Hardware Setup

### Pin Connections (without HAT)

Check your LED matrix info sheet.
For Waveshare matrix see https://www.waveshare.com/wiki/RGB-Matrix-P2.5-64x32

**Important:** Use multiple GND connections for stability!

## Usage

### Run manually
```bash
sudo python3 main.py
```

## Troubleshooting

### Display flickers
- **Use shorter cables** (<20cm) or get an **RGB Matrix HAT with buffers**
- Increase `gpio_slowdown`:
  ```python
  options.gpio_slowdown = 4  # Try 4, 5, 6
  ```
- Avoid breadboards for permanent installation

### "No data received"
- Check internet connection: `ping 8.8.8.8`
- Test API directly:
  ```bash
  curl "https://v6.db.transport.rest/stops/130637/departures?duration=120"
  ```
- Check firewall/network restrictions

### Wrong station IDs
- Find your station:
  ```bash
  curl "https://v6.db.transport.rest/locations?query=Hauptbahnhof%20Leipzig"
  ```

### Display shows nothing
- Check wiring (especially GND connections)
- Verify matrix works:
  ```bash
  cd ~/rpi-rgb-led-matrix/examples-api-use
  sudo ./demo -D0
  ```
- Check font path in `led_matrix_display.py`

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Hardware Setup](docs/HARDWARE_SETUP.md)
- [Configuration Options](docs/CONFIGURATION.md)

## Customization Examples

### Add more lines
```python
TRAM_FILTER = {
    "STR 15": ["Meusdorf"],
    "STR 8": ["Sellerhausen"],
    "STR 11": ["Schkeuditz"],     # Add more lines
    "STR N2": ["Hauptbahnhof"]
}
```

### Change colors
```python
LINE_COLORS = {
    "Bus 60": (255, 0, 0),     # Red
    "STR 8": (0, 255, 0),      # Green
    "STR 15": (0, 0, 255),     # Blue
}
```

### Adjust brightness by time
```python
from datetime import datetime

hour = datetime.now().hour
if 6 <= hour < 22:
    brightness = 50  # Daytime
else:
    brightness = 20  # Nighttime

lcd = LEDMatrixDisplay(brightness=brightness)
```

## Technical Details

### API
Uses [Deutsche Bahn HAFAS API](https://v6.db.transport.rest/) (unofficial):
- Endpoint: `https://v6.db.transport.rest`
- No API key required
- Rate limit: Be reasonable (~1 request/minute)

### Performance
- CPU usage: ~70% on Raspberry Pi 3B+ (ok for LED matrices)
- Memory: ~50MB
- Network: ~2KB per API request

### Display Update Logic
```
API Request (every 60s) -> Store absolute departure times ->

-> Display Update (every 20s) -> Calculate minutes from stored times
                             -> Smooth countdown without API spam!
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Add later?
- [ ] Weather display integration
- [ ] Larger matrices (128x64)
- [ ] Alternative fonts
- [ ] Brightness auto-adjustment (light sensor)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) by Henner Zeller - Excellent LED matrix library
- [Deutsche Bahn HAFAS API](https://v6.db.transport.rest/) - Public transport data
- [Adafruit](https://www.adafruit.com/) - RGB Matrix HAT and documentation

## Contact

Questions? Open an issue or reach out!

## Star History

If this project helped you, please consider giving it a star!
