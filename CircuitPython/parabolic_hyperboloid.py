""" CircuitPython sample code based on Adafruit's Simple FancyLED
    example for NeoPixel strip
"""

import board
import time
import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy
import adafruit_fancyled.fastled_helpers as helper

num_leds = 40
half_leds = num_leds//2
quarter_leds = num_leds//4

# Declare a 6-element RGB rainbow palette
palette = [
    fancy.CRGB(1.0, 0.0, 0.0),  # Red
    fancy.CRGB(0.5, 0.5, 0.0),  # Yellow
    fancy.CRGB(0.0, 1.0, 0.0),  # Green
    fancy.CRGB(0.0, 0.5, 0.5),  # Cyan
    fancy.CRGB(0.0, 0.0, 1.0),  # Blue
    fancy.CRGB(0.5, 0.0, 0.5),  # Magenta
]


heatmap_gp = bytes([
    0, 255, 255, 255,  # White
    64, 255, 255, 0,  # Yellow
    128, 255, 0, 0,  # Red
    255, 0, 0, 0])  # Black
# fmt: on

ocean_gp = bytes([
    0, 255, 255, 255, # white
    64, 0, 0, 255,    # blue
    128, 0, 255, 255, # cyan
    192, 0, 255, 0,   # green
    255, 0, 0, 0])   # black

# Convert the gradient palette into a normal palette w/16 elements:
heat_palette = helper.loadDynamicGradientPalette(heatmap_gp, 16)
ocean_palette = helper.loadDynamicGradientPalette(ocean_gp, 16)


# Declare a NeoPixel object on pin D6 with num_leds pixels, no auto-write.
# Set brightness to max because we'll be using FancyLED's brightness control.
pixels = neopixel.NeoPixel(board.D6, num_leds, brightness=1.0, auto_write=False)

offset = 0  # Positional offset into color palette to get it to 'spin'
heat_offset = 0

def rainbow_flush(delay=.02):
    global offset
    for i in range(num_leds):
        # Load each pixel's color from the palette using an offset, run it
        # through the gamma function, pack RGB value and assign to pixel.
        color = fancy.palette_lookup(palette, offset + i / num_leds)
        color = fancy.gamma_adjust(color, brightness=0.25)
        pixels[i] = color.pack()
    pixels.show()
    time.sleep(delay)
    offset += 0.02  # Bigger number = faster spin


def heat_animation(delay=0.02):
    global heat_offset
    for i in range(num_leds):
        # Load each pixel's color from the palette.  FastLED uses 16-step
        # in-between blending...so for a 16-color palette, there's 256
        # steps total.  With 10 pixels, multiply the pixel index by 25.5
        # (and add our offset) to get FastLED-style palette position.
        color = helper.ColorFromPalette(heat_palette, int(heat_offset + i * 25.5), blend=True)
#        color = helper.ColorFromPalette(ocean_palette, int(heat_offset + i * 6.375), blend=True)
        # Apply gamma using the FastLED helper syntax
        color = helper.applyGamma_video(color)
        # 'Pack' color and assign to NeoPixel #i
        pixels[i] = color.pack()
    pixels.show()
    time.sleep(delay)
    heat_offset += 8  # Bigger number = faster spin

def simple_rainbow(delay = .03):
    global offset
    num_steps = 4
    for i in range(num_steps):
        color = fancy.palette_lookup(palette, offset + i / num_steps)
        color = fancy.gamma_adjust(color, brightness=0.25)
        col = color.pack()
        nleds = num_leds//num_steps
        start = i*nleds
        for j in range(start,start+nleds,1):
            pixels[j] = col

    pixels.show()
    offset += .02
    time.sleep(delay)

def opposite(n):
    if ((n//10) % 2):
        return 49 - n
    else:
        return 29 - n

walk_index = 0
def simple_walk(delay=0.05):
    global walk_index, offset

    trail_length = 4
    color = fancy.palette_lookup(palette, offset)
    oppcol = fancy.palette_lookup(palette, offset+0.5)
    for i in range(trail_length):
        index = (walk_index + i) % num_leds
        index2 = (index + 10) % num_leds
        opp_index = opposite(index)
        opp_index2 = opposite(index2)
        bright = 1.0/(trail_length - i)
        pixels[index] = fancy.gamma_adjust(color, brightness = bright).pack()
        pixels[opp_index] = pixels[index]
        pixels[index2] = fancy.gamma_adjust(oppcol, brightness = bright).pack()
        pixels[opp_index2] = pixels[index2]
    pixels.show()
    time.sleep(delay)
    pixels[walk_index] = (0,0,0)
    pixels[opposite(walk_index)] = (0,0,0)
    index2 = (walk_index + 10) % num_leds
    pixels[index2] = (0,0,0)
    pixels[opposite(index2)] = (0,0,0)
    walk_index = (walk_index + 1) % num_leds
    offset = offset + .02



current_animation = 0
last_switch_time = time.monotonic()
animation_run_time = 5
anims = [heat_animation, rainbow_flush, simple_rainbow, simple_walk]

while True:
    if (time.monotonic() - last_switch_time) > animation_run_time:
        current_animation = (current_animation + 1) % len(anims)
        pixels.fill((0,0,0))
        last_switch_time = time.monotonic()
    anims[current_animation]()