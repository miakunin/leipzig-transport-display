# Installation Guide

Complete installation guide for Leipzig Transport Display with Docker support.

## Overview

This guide covers two installation methods:

1. **Docker (Recommended)** - Clean, isolated, easy updates
2. **Native Python** - Direct installation, manual dependencies

---

## Method 1: Docker Installation (Recommended)

Docker provides clean isolation and easy updates without polluting your system.

### Prerequisites

- Raspberry Pi OS (32-bit or 64-bit)
- SSH or direct access to Pi
- Internet connection

### Step 1: Install Docker

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (no more sudo!)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install -y docker-compose

# Logout and login for group changes
# Or reboot:
sudo reboot
```

**Verify Docker:**
```bash
docker --version
docker-compose --version

# Test (after reboot):
docker run hello-world
```

### Step 2: Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/leipzig-transport-display.git
cd leipzig-transport-display
```

### Step 3: Configure Your Stations

**Option A: Create config_local.py (Recommended)**

```bash
# Copy example
cp config_example.py config_local.py

# Edit with your settings
nano config_local.py
```

Edit:
```python
BUS_STATION_ID = "YOUR_STATION_ID"
TRAM_STATION_ID = "YOUR_STATION_ID"

BUS_FILTER = {
    "Bus XX": ["Your Destination"]
}

TRAM_FILTER = {
    "STR YY": ["Your Destination"]
}
```

**Option B: Edit main.py directly**

```bash
nano main.py
# Edit lines 19-50 with your configuration
```

See [CONFIGURATION.md](CONFIGURATION.md) for finding station IDs.

### Step 4: Build and Run

```bash
# Build Docker image (first time, takes 5-10 minutes)
docker-compose build

# Start the container
docker-compose up -d

# Check logs
docker-compose logs -f
```

**Expected output:**
```
leipzig-bus  | Leipzig Transport Display - Multi-Color Version
leipzig-bus  | Display updates: every 20s
leipzig-bus  | API updates: every 60s
leipzig-bus  | OK! Loaded configuration from config_local.py
leipzig-bus  | Initializing LED Matrix...
leipzig-bus  | OK LED Matrix initialized: 64x32, brightness=50%
leipzig-bus  | [15:30:45] Fetching data from API...
leipzig-bus  |   OK! Bus: Bus 60 at 15:35
leipzig-bus  |   OK! Trams: 3 departures
```

### Step 5: Verify Display

The LED matrix should now show your departures!

```
┌────────────────┐
│ Bus80   5m     │
│ STR12  now     │
│ STR7   12m     │
│ STR12  18m     │
└────────────────┘
```

### Docker Commands Cheat Sheet

```bash
# Start container
docker-compose up -d

# Stop container
docker-compose stop

# Restart after code changes
docker-compose restart

# View logs
docker-compose logs -f

# Stop and remove container
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Check status
docker-compose ps
```

### Auto-start on Boot

Docker container already has `restart: unless-stopped` in `docker-compose.yml`.

**Enable Docker to start on boot:**
```bash
sudo systemctl enable docker
```

Container will:
- Start automatically on boot
- Restart if it crashes
- Stop only when you run `docker-compose down`

---

## Method 2: Native Python Installation

Direct installation without Docker. More control but requires manual dependency management.

### Step 1: Install System Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install build tools
sudo apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libfreetype6-dev \
    libopenjp2-7-dev
```

### Step 2: Install RGB LED Matrix Library

This is the core library for controlling LED matrices.

```bash
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix

# Build the library
make build-python PYTHON=$(which python3)

# Install Python bindings
sudo make install-python PYTHON=$(which python3)

# Verify installation
python3 -c "from rgbmatrix import RGBMatrix; print('OK')"
```

### Step 3: Clone Project

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/leipzig-transport-display.git
cd leipzig-transport-display
```

### Step 4: Install Python Dependencies

```bash
pip3 install -r requirements.txt

# Or manually:
pip3 install requests
```

### Step 5: Configure Your Stations

```bash
# Option A: Create config_local.py
cp config_example.py config_local.py
nano config_local.py

# Option B: Edit main.py
nano main.py
```

See [CONFIGURATION.md](CONFIGURATION.md) for details.

### Step 6: Test Run

```bash
# Must run as root (for GPIO access)
sudo python3 main.py
```

**Expected output:**
```
==================================================
Leipzig Transport Display - Multi-Color Version
==================================================
Display updates: every 20s
API updates: every 60s
==================================================
OK! Loaded configuration from config_local.py
Initializing LED Matrix...
OK Font loaded successfully!
OK LED Matrix initialized: 64x32, brightness=50%

Initial data fetch (will retry until success)...
[15:30:45] Fetching data from API...
  OK! Bus: Bus 80 at 15:35
  OK! Trams: 3 departures
    - STR 12 at 15:32
    - STR 7 at 15:38

OK! Initial data received!

Starting update loop...
```

Press `Ctrl+C` to stop.

---

## Post-Installation

### Verify Everything Works

**1. Check API connectivity:**
```bash
curl "https://v6.db.transport.rest/stops/YOUR_STATION_ID/departures?duration=120"
```

**2. Check display:**
- Text visible?
- Colors correct?
- No flickering?

**3. Check updates:**
```bash
# Watch logs
docker-compose logs -f
# or for native:
sudo journalctl -u leipzig-display -f

# Should see:
[15:31:05] Fetching data from API...
[15:31:25] Display updated:
```

### Adjust Brightness

**Docker:**
```bash
# Edit main.py
nano main.py

# Find and change:
lcd = LEDMatrixDisplay(brightness=40)  # 0-100

# Restart
docker-compose restart
```

**Native:**
```bash
nano main.py
# Edit brightness
sudo systemctl restart leipzig-display
```

### Update Display Intervals

```bash
# Edit main.py
nano main.py

# Find and change:
DISPLAY_UPDATE_INTERVAL = 20  # seconds
API_UPDATE_INTERVAL = 60      # seconds

# Restart
docker-compose restart
# or
sudo systemctl restart leipzig-display
```

---

## 🐛 Common Installation Issues

### "Permission denied" errors

```bash
# Docker not starting
sudo usermod -aG docker $USER
# Then logout/login

# GPIO access denied
sudo python3 main.py  # Must use sudo!
```

### "Cannot find font file"

```bash
# Download font manually
cd ~/rpi-rgb-led-matrix
wget https://github.com/hzeller/rpi-rgb-led-matrix/raw/master/fonts/6x10.bdf -O fonts/6x10.bdf
```

### "No module named 'rgbmatrix'"

**Docker:** Shouldn't happen (built into container)

**Native:**
```bash
cd ~/rpi-rgb-led-matrix
sudo make install-python PYTHON=$(which python3)
```

### Display shows nothing

1. Check hardware connections
2. Verify matrix powers on (power LED)
3. Test with demo:
   ```bash
   cd ~/rpi-rgb-led-matrix/examples-api-use
   sudo ./demo -D0
   ```

### "No data received" from API

```bash
# Test internet
ping 8.8.8.8

# Test API
curl "https://v6.db.transport.rest/stops/008010205/departures?duration=120"

# Check station ID is correct
```

---

Your display should now be running and showing real-time departures!
