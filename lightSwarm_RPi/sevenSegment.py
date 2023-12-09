import RPi.GPIO as GPIO
import time
import threading   

SDI_7SEG = 19   # Serial Data for 7 segment display
SRCLK_7SEG = 13 # Serial Clock for 7 segment display
RCLK_7SEG = 26  # Register Clock for 7 segment display

# Pins connected to each digit in the 4 digit seven segment display
digitPins = [10, 22, 27, 17]

# Values corresponding to each digit (0 to 9)
DIGITS = [0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90]

CLEAR_DISPLAY = 0xFF

def hc595_send_data_7segment(data): 
    for i in range(8):
        GPIO.output(SDI_7SEG, 0x80 & (data << i))
        GPIO.output(SRCLK_7SEG, GPIO.HIGH)
        GPIO.output(SRCLK_7SEG, GPIO.LOW)
    GPIO.output(RCLK_7SEG, GPIO.HIGH)
    GPIO.output(RCLK_7SEG, GPIO.LOW)

def pickDigit(digit):
    for i in digitPins:
        GPIO.output(i, GPIO.LOW)
    GPIO.output(digitPins[digit], GPIO.HIGH)

data_7seg = 0

def set_7segment():
    global data_7seg                    
    while True:
        set_data(data_7seg) 
        # time.sleep(0.001)   

def set_data(data):
    hc595_send_data_7segment(CLEAR_DISPLAY)
    pickDigit(0)  
    hc595_send_data_7segment(DIGITS[data % 10])

    hc595_send_data_7segment(CLEAR_DISPLAY)
    pickDigit(1)
    hc595_send_data_7segment(DIGITS[data % 100 // 10])

    hc595_send_data_7segment(CLEAR_DISPLAY)
    pickDigit(2)
    hc595_send_data_7segment(DIGITS[data % 1000 // 100])

    hc595_send_data_7segment(CLEAR_DISPLAY)
    pickDigit(3)
    hc595_send_data_7segment(DIGITS[data % 10000 // 1000])

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(SDI_7SEG, GPIO.OUT)
    GPIO.setup(RCLK_7SEG, GPIO.OUT)
    GPIO.setup(SRCLK_7SEG, GPIO.OUT)

    for i in digitPins:
        GPIO.setup(i, GPIO.OUT) 