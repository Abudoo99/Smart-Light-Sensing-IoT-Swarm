import RPi.GPIO as GPIO
import time
import threading
import random

SDI_MAT = 8
SRCLK_MAT = 7
RCLK_MAT = 5

PLOT_ROW_SIZE = 4

# Rows indicating each row in the LED matrix
ROWS = [1,2,3,4,5,6,7,8]

# Pin numbers of GPIO pins controlling columns of LED Matrix
COLS_CTL = [18, 23, 24, 25, 12, 16, 20, 21]

# Send data from shift register to LED Matrix
def hc595_send_data_matrix(data):
    for bit in range(8): 

        # Sending data of corresponding bit
        GPIO.output(SDI_MAT, 0x80 & (data << bit))
        
        # Shifting previous bit and storing current bit in the register
        GPIO.output(SRCLK_MAT, GPIO.HIGH)
        GPIO.output(SRCLK_MAT, GPIO.LOW)

    # Pushing the 8bit value to output
    GPIO.output(RCLK_MAT, GPIO.HIGH)
    GPIO.output(RCLK_MAT, GPIO.LOW)

# Clearing the LED Matrix
def matrix_clear():
    for i in range(8):
        GPIO.output(COLS_CTL[i], 0)

    hc595_send_data_matrix(0xFF)

# Sending data to rows of the LED matrix
def set_row(row_num):
    row_val = 0x00
    for i in range(row_num):
        row_val = row_val | (1 << i)

    #print("%x" % (255- row_val))
    hc595_send_data_matrix(0xFF - row_val)

# Sending data to columns of the LED matrix
def set_column(col_num):
    GPIO.output(COLS_CTL[col_num], 1)

# Turning ON LED Matrix based on sensor data received
def set_data(row, col):
    set_column(col)
    set_row(row)
    # time.sleep(0.0001)
    matrix_clear()

# Mapping sensor data to its corresponding row in the LED matrix
def map_sensor_data_to_row(sensor_value):
    if sensor_value == 0:
        return -1
    elif sensor_value in range(1, 128):
        return ROWS[0] 
    elif sensor_value in range(128, 255):
        return ROWS[1]
    elif sensor_value in range(255, 383):
        return ROWS[2]
    elif sensor_value in range(383, 511):
        return ROWS[3]
    elif sensor_value in range(511, 639):
        return ROWS[4]
    elif sensor_value in range(639, 767):
        return ROWS[5]
    elif sensor_value in range(767, 895):
        return ROWS[6]
    elif sensor_value > 895:
        return ROWS[7]

data_mat = []
sensor_values = []

def set_LED_matrix():
    global data_mat
    while True:
        # data_mat = data_mat[-8:]
        for index in range(len(data_mat)):
            set_data(data_mat[index], index)
        # time.sleep(0.001)
        # print(data)

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Configuring GPIO pins for LED matrix 

    for i in range(len(COLS_CTL)):
        GPIO.setup(COLS_CTL[i], GPIO.OUT)

    GPIO.setup(SDI_MAT, GPIO.OUT)
    GPIO.setup(SRCLK_MAT, GPIO.OUT)
    GPIO.setup(RCLK_MAT, GPIO.OUT)
    GPIO.output(SDI_MAT, GPIO.LOW)
    GPIO.output(RCLK_MAT, GPIO.LOW)
    GPIO.output(SRCLK_MAT, GPIO.LOW)
