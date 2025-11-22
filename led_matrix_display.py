#!/usr/bin/env python3
"""
LED Matrix display driver for 64x32 RGB panels
"""
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import os


class LEDMatrixDisplay:
    """
    Driver for RGB LED Matrix displays via HUB75 interface
    
    Supports 64x32 P2.5 matrices with 4 lines of text display
    """
    
    def __init__(self, rows=32, cols=64, brightness=30, default_color=(255, 255, 0)):
        """
        Initialize LED matrix
        
        Args:
            rows: Number of rows (32)
            cols: Number of columns (64)
            brightness: Brightness 0-100 (30 recommended for home use)
            rotation: Rotation in degrees (0, 180 only supported)
                     0   = Normal
                     180 = Upside down (переворот)
            default_color: Default RGB color tuple (255, 255, 0) = Yellow
        """
        print("Initializing LED Matrix...")

        # Matrix configuration
        options = RGBMatrixOptions()
        options.rows = rows
        options.cols = cols
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'regular'
        options.brightness = brightness
        options.gpio_slowdown = 4
        options.disable_hardware_pulsing = True
       
        # Create matrix
        self.matrix = RGBMatrix(options=options)
        
        # Store default color
        self.default_color = default_color
        
        # Load font
        # Try multiple possible font paths
        font_paths = [
            "/usr/share/fonts/rpi-rgb-led-matrix/6x10.bdf",
            "./fonts/6x10.bdf",
        ]
        
        font_loaded = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                print(f"Loading font from: {font_path}")
                self.font = graphics.Font()
                self.font.LoadFont(font_path)
                font_loaded = True
                print("OK Font loaded successfully!")
                break
        
        if not font_loaded:
            print("⚠ Warning: Could not find font file!")
            print("Searched paths:")
            for path in font_paths:
                print(f"  - {path}")
            # Create a basic font object anyway
            self.font = graphics.Font()
        
        self.width = cols
        self.height = rows
        
        print(f"OK LED Matrix initialized: {cols}x{rows}, brightness={brightness}%")
        
    def clear(self):
        """Clear the display"""
        self.matrix.Clear()
        
    def write_lines(self, lines, colors=None):
        """
        Write lines to the matrix
        
        Args:
            lines: List of strings or list of dicts for multi-color
            colors: List of RGB tuples (only for simple strings)
        """
        self.matrix.Clear()
        
        y_offset = 7  # Starting position (font is 6x9, baseline at 7)
        line_height = 8  # Space between lines
        

        for i, line in enumerate(lines[:4]):  # Max 4 lines for 32 pixels
            if not line:
                continue
    
            # Calculate Y position
            y_pos = y_offset + (i * line_height)

            # Check if line is dict with segments (multi-color)
            if isinstance(line, dict) and 'segments' in line:
                x_pos = 2  # Start position
                
                for segment in line['segments']:
                    seg_text = segment['text']
                    seg_color = segment['color']
                    color_obj = graphics.Color(seg_color[0], seg_color[1], seg_color[2])
                    
                    # Draw this segment
                    graphics.DrawText(
                        self.matrix,
                        self.font,
                        x_pos,
                        y_pos,
                        color_obj,
                        seg_text
                    )
                    
                    # Move x position for next segment
                    x_pos += len(seg_text) * 5
            
            # Simple string (single color)
            elif isinstance(line, str):
                text = line[:10] if len(line) > 10 else line
                
                # Get color
                if colors and i < len(colors):
                    color = colors[i]
                else:
                    color = self.default_color
                
                color_obj = graphics.Color(color[0], color[1], color[2])
                
                # Draw text
                graphics.DrawText(
                    self.matrix,
                    self.font,
                    2,  # x position (left margin)
                    y_pos,
                    color_obj,
                    text
                )
        
    def set_brightness(self, brightness):
        """
        Adjust brightness
        
        Args:
            brightness: 0-100
        """
        self.matrix.brightness = brightness
        
    def close(self):
        """Clean up and close"""
        self.matrix.Clear()
        print("LED Matrix closed.")
