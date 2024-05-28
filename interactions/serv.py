import socket
import time
import threading
from rpi_ws281x import *
import json

HOST = "127.0.0.1"
PORT = 65432

# LED strip configuration:
LED_COUNT      = 144     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 65      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Colors:
R, G, B = 28, 115, 255
BLUE = Color(R, G, B)

def clear(strip: Adafruit_NeoPixel):
    # Clear the light strip
    for i in range(0, LED_COUNT):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

def set_solid(strip: Adafruit_NeoPixel, color = BLUE, start_led = None, stop_led = None):
    # Set portion of the light strip or the entire light strip to a color
    if start_led is None or stop_led is None:
        start_led, stop_led = 0, strip.numPixels() - 1
    for i in range(start_led, stop_led+1):
        strip.setPixelColor(i, color)
    
    strip.show()

def colorwipe(strip: Adafruit_NeoPixel, direction, color=BLUE, delay=0.01):
    # For directional movement and reverse
    clear(strip)

    match direction:
        case "right":
            for i in range(strip.numPixels()//2,  strip.numPixels()):
                start = time.monotonic()
                strip.setPixelColor(i, color)
                strip.show()
                while(time.monotonic() <= start + delay): pass
        
        case "left":
            for i in range(strip.numPixels()//2 - 1, -1, -1):
                start = time.monotonic()
                strip.setPixelColor(i, color)
                strip.show()
                while(time.monotonic() <= start + delay): pass
        
        case "reverse":
            for i in range(strip.numPixels()//2):
                start = time.monotonic()
                strip.setPixelColor(strip.numPixels()//2 + i, color)
                strip.setPixelColor(strip.numPixels()//2 - 1 - i, color)
                strip.show()
                while(time.monotonic() <= start + delay): pass
        
        case "straight":
            for i in range(strip.numPixels()//2):
                start = time.monotonic()
                strip.setPixelColor(i, color)
                strip.setPixelColor(strip.numPixels() - 1 - i, color)
                strip.show()
                while(time.monotonic() <= start + delay): pass
        

def strobe(strip: Adafruit_NeoPixel, color = BLUE, delay=0.2):
    # For when the robot approaches users not facing at the robot (gain attention)
    clear(strip)
    start = time.monotonic()
    set_solid(strip, color)
    strip.show()
    while(time.monotonic() <= start + delay): pass

    start = time.monotonic()
    clear(strip)
    strip.show()
    while(time.monotonic() <= start + delay): pass


def theaterChase(strip: Adafruit_NeoPixel, color = BLUE, delay=0.2):
    """Movie theater light style chaser animation."""
    for q in range(3):
        start = time.monotonic()
        for i in range(0, strip.numPixels(), 3):
            strip.setPixelColor(i+q, color)
        strip.show()
        while(time.monotonic() <= start + delay): pass
        for i in range(0, strip.numPixels(), 3):
            strip.setPixelColor(i+q, 0)


strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()
set_solid(strip)
strip.show()


def pattern_handler(data_func):
    while True and data_func() != "q":
        print(data_func())
        if data_func() == "u-1":
            colorwipe(strip, "reverse")
        elif data_func() == "u-2":
            colorwipe(strip, "right")
        elif data_func() == "c":
            clear(strip)
        elif data_func() == "b":
            strobe(strip)
        elif data_func() == "n":
            theaterChase(strip)
        elif data_func() == "m":
            set_solid(strip)
        elif data_func() == "y-1":
            colorwipe(strip, "reverse")
        elif data_func() == "y-2":
            colorwipe(strip, "straight")
        time.sleep(1)
    
    clear(strip)



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    data = "-"

    def data_func():
        return data
    
    worker = threading.Thread(target=pattern_handler, args=(data_func,))
    worker.start()

    while True:
        data = conn.recv(1024).decode()
        if data == "q":
            break
    
    conn.close()
            