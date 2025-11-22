# Hardware Setup Guide

Complete wiring guide for RGB LED Matrix on Raspberry Pi.

## Required Hardware

### Essential Components

| Component | Specification |
|-----------|--------------|
| **Raspberry Pi** | 3B+ or newer (3A+, 4, 5, Zero 2W) |
| **RGB LED Matrix** | 64x32, P2.5 or P3, HUB75 interface |
| **Power Supply (RPi)** | 5V 2.5A+ (official recommended) |
| **Power Supply (LED)** | 5V 3-4A+ (separate!) |
| **MicroSD Card** | 16GB+ Class 10 |

ESP32 should work fine too!

### Connection Options

**Option A: Direct Wiring (Testing Only)**
- 20-30x Female-Female Dupont wires
- **Causes flickering!** Max cable length: 20cm

**Option B: RGB Matrix HAT (Recommended)**
- Adafruit RGB Matrix HAT or similar with **74HCT245 buffers**
- **Eliminates flickering!**

---

## Option A: Direct Wiring (No HAT)

### Pin Connections

Check your LED matrix info!

**Waveshare 64x32 LED Matrix → Raspberry Pi GPIO**

See https://www.waveshare.com/wiki/RGB-Matrix-P2.5-64x32

### Critical Notes for Direct Wiring

**IMPORTANT:**
1. **Multiple GND connections** - Use at least 4-6 GND wires for stability
2. **Short cables** - Maximum 15-20cm, shorter is better
3. **Avoid breadboards** - They add resistance and could cause flickering
4. **No splitters** - One wire per pin, no Y-splitters
5. **Avoid USB power** - Use official 5V power supply

### Wiring Process

**Step 1: Power OFF everything**
```bash
sudo shutdown -h now
# Wait for RPi to power off
# Disconnect power from both RPi and LED matrix
```

**Step 2: Connect GND first**
- Connect 4-6 GND wires from matrix to RPi GND pins
- This is the most important connection!

**Step 3: Connect data pins**
- Connect R1, G1, B1
- Connect R2, G2, B2
- Connect A, B, C, D
- Connect CLK, LAT, OE

**Step 4: Double-check**
```
All pins connected?
No loose wires?
GND connections solid?
No short circuits (wires touching)?
```

**Step 5: Power on LED matrix separately**
- Connect 5V power supply to LED matrix (5V 3-4A)
- Check if power LED lights up

**Step 6: Power on Raspberry Pi**
- Connect RPi power supply (5V 2.5A)
- Boot up and test

---

## Option B: RGB Matrix HAT (Recommended)

### What is an RGB Matrix HAT?

An add-on board that sits on top of Raspberry Pi GPIO pins with:
- Level shifters (74HCT245 chips)
- Buffer circuits for clean signals
- Screw terminals for easy wiring
- Eliminates flickering completely

### Installation

**Step 1: Assemble HAT**
```
1. Solder 40-pin header to HAT (if not pre-soldered)
2. Solder screw terminals (if not pre-soldered)
3. Optional: Solder power connectors
```

**Step 2: Mount on Raspberry Pi**
```
1. Power OFF Raspberry Pi
2. Align 40-pin header with RPi GPIO
3. Press down firmly (all pins must connect)
4. Optional: Use standoffs to secure
```

**Step 3: Connect LED Matrix**
```
1. Use ribbon cable (usually included with matrix)
   Matrix HUB75 port → HAT HUB75 connector
   
2. Or wire to screw terminals
```

**Step 4: Power**
```
Option A: Separate power supplies (recommended)
  - RPi: 5V 2.5A
  - LED Matrix: 5V 3-4A

Option B: Shared power (if HAT supports it)
  - 5V 5A power supply to HAT
  - HAT powers both RPi and matrix
```

---

## Power Supply Setup

### Critical Power Requirements

**Raspberry Pi:**
- Voltage: 5V ±5%
- Current: 2.5A minimum (3A recommended for Pi 4/5)
- **Use official power supply!**

**LED Matrix 64x32:**
- Voltage: 5V ±5%
- Current: 2-4A (depends on brightness and content)
- Full white at 100% brightness: ~4A
- Normal usage (50% brightness, mixed colors): ~2-3A

### Power Calculation

```
Maximum power = 64 pixels × 32 pixels × 3 colors × 20mA = 4A

Typical usage:
- 50% brightness: ~2A
- Mixed colors (not all white): ~1.5-2A
- Low brightness (30%): ~1A
```

**!!!Warning:** Don't power LED matrix from Raspberry Pi GPIO pins!
- GPIO pins max: 50mA total
- LED matrix needs: 2000-4000mA
- Result: **Instant damage!**

### Connecting Power

**LED Matrix Power Connector:**
```
Most matrices have:
- Red wire: +5V
- Black wire: GND

Connect to 5V 4A power supply
```

**Ground Connection:**
- LED matrix GND **must** connect to RPi GND
- Use multiple GND wires (4-6 connections)
- This ensures signals have common reference

---

## Testing Your Setup

### Step 1: Verify GPIO Access

```bash
# Install GPIO tools
sudo apt-get install python3-rpi.gpio

# Test GPIO
python3 -c "import RPi.GPIO as GPIO; print('GPIO OK')"
```

### Step 2: Test LED Matrix Library

```bash
cd ~/rpi-rgb-led-matrix/examples-api-use
sudo ./demo -D0

# Should show demo patterns
# Press Ctrl+C to stop
```

### Step 3: Test Our Application

```bash
cd ~/leipzig-transport-display
sudo python3 main.py

# Should show departures
# Check for:
API fetches working
Display shows text
No flickering
Colors correct
```

---

## Troubleshooting Hardware

### Display flickers badly

**Causes:**
1. Cables too long (>20cm)
2. Breadboard used (adds resistance)
3. Poor GND connections
4. Interference from WiFi/Bluetooth

**Solutions:**
- Use RGB Matrix HAT (eliminates 99% of flickering)
- Shorten cables to <15cm
- Add more GND connections (4-6 wires)
- Increase `gpio_slowdown` in code:
  ```python
  options.gpio_slowdown = 4  # Try 4, 5, or 6
  ```

### Display shows garbage/noise

**Causes:**
- Wrong pin connections
- Loose wires
- Insufficient power

**Solutions:**
```bash
# 1. Power OFF
sudo shutdown -h now

# 2. Check ALL connections
- Verify each pin against pinout table
- Re-seat any loose connectors
- Check for bent pins

# 3. Check power supply
- Must be 5V (not 5.2V or 4.8V)
- Must provide enough current (4A for matrix)

# 4. Test matrix separately
- Connect only power to matrix
- Power LED should light up
```

### Display is dim

**Causes:**
- Brightness set too low
- Insufficient power
- PWM frequency too low

**Solutions:**
```python
# Increase brightness
lcd = LEDMatrixDisplay(brightness=80)  # 0-100

# Check power supply
# 5V 4A minimum(!) for 64x32 matrix
```

### Colors are wrong

**Causes:**
- Swapped R/G/B connections
- Wrong matrix type in code

**Solutions:**
```bash
# 1. Check cable connections
# 2. Try different hardware mapping
options.hardware_mapping = 'adafruit-hat'  # If using HAT
# or
options.hardware_mapping = 'regular'  # Direct wiring
```

### Raspberry Pi won't boot with matrix connected

**Causes:**
- Short circuit
- Matrix drawing power from GPIO

**Solutions:**
```bash
# 1. Disconnect matrix completely
# 2. Boot Raspberry Pi
# 3. Check for:
- Bent pins
- Wires touching each other
- Matrix power connected to RPi GPIO (wrong!)

# 4. Fix issues
# 5. Connect matrix again (powered OFF)
# 6. Boot RPi
# 7. Power ON matrix separately
```

---

### Libraries

- rpi-rgb-led-matrix: https://github.com/hzeller/rpi-rgb-led-matrix
- Excellent documentation and examples

---

## ⚡ Safety Notes

- **Never connect >5V** to Raspberry Pi GPIO
- **Don't power LED from RPi GPIO** pins
- Always connect **GND first**, disconnect **GND last**
- **Power OFF** when connecting/disconnecting wires
- Use proper **5V power supplies** (not USB chargers)
- Don't touch pins while powered on

---
