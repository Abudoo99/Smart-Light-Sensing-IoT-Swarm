'''
    Smart Light Sensing IoT Swarm
    Author  :   Abyukth Kumar
'''
import signal
import sys
import time
import datetime

import threading
import RPi.GPIO as GPIO

from netifaces import interfaces, ifaddresses, AF_INET
from socket import *

# Source code consisting of functions related to LED Matrix and 7 segment display
import ledMatrix
import sevenSegment

import logging

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

current_datetime = datetime.datetime.now()
global_log_filename = f'swarm_data_{current_datetime.strftime("%Y%m%d_%H%M%S")}.log'

BUTTON_GPIO = 15

#Yellow LED to indicate RESET
Y_LED = 6

VERSIONNUMBER = 11

# packet type definitions
LIGHT_UPDATE_PACKET = 0
RESET_SWARM_PACKET = 1
DEFINE_SERVER_LOGGER_PACKET = 2
LOG_TO_SERVER_PACKET = 3

MYPORT = 1999

SWARMSIZE = 6
SEND_SERVER_PACKET = 10

logString = ""

logFlag = False     # Flag indicating start of sensor data logging

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def change_log_file(filename):
    for handler in logger.handlers[:]:  # remove all old handlers
        logger.removeHandler(handler)
    file_handler = logging.FileHandler(filename)  # create new handler
    logger.addHandler(file_handler)

def button_pressed_callback(channel):
    global logFlag, sensor_data, global_log_filename

    logFlag = True

    current_datetime = datetime.datetime.now()
    print("Old Log File : ",global_log_filename)
    global_log_filename = f'swarm_data_{current_datetime.strftime("%Y%m%d_%H%M%S")}.log'

    change_log_file(global_log_filename)

    SendRESET_SWARM_PACKET(s)

    GPIO.output(Y_LED, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(Y_LED, GPIO.LOW)

log_master_start_time = 0
master_end_time = 0
master_log_time = 0
log_last_ip = 0
master_total_run_time = 0

def buildWebMapToFile(logString, swarmSize):

    global log_master_start_time,master_end_time,master_log_time,log_last_ip, swarmElement
    swarmList = logString.split("|")
    log_only_master = True
    for i in range(0,swarmSize):
        swarmElement = swarmList[i].split(",")	
        # print("swarmElement=", swarmElement)			
			
        if (swarmElement[4] == "PR"):
            if (swarmElement[1] == "1"):
                if log_last_ip == 0:
                    log_master_start_time = datetime.datetime.now()
                    master_log_time = log_master_start_time
                    log_last_ip = swarmElement[5]
                    master_total_run_time = master_log_time - log_master_start_time
                else:
                    if log_last_ip == swarmElement[5]:
                        master_log_time = datetime.datetime.now()
                        master_total_run_time = master_log_time - log_master_start_time
                    else:
                        log_master_start_time = datetime.datetime.now()
                        master_log_time = log_master_start_time
                        master_total_run_time = master_log_time - log_master_start_time
                        log_last_ip = swarmElement[5]
   #                     logging.info(f'LDR value: {0}, IP address: {log_last_ip},Master StartTime :{log_master_start_time}, master_log_time: {master_log_time}, master_total_run_time: {master_total_run_time}, Raw data: {0}')
                if logFlag == True and log_only_master == True:
                    print("Log Successful")
                 #   logger.info(f'LDR value: {swarmElement[3]}, IP address: {swarmElement[5]},master_start_time: {log_master_start_time}, master_log_time: {master_log_time}, master_total_run_time: {master_total_run_time}, Raw data: {swarmElement}')
                    message = f'LDR value: {swarmElement[3]}, IP address: {swarmElement[5]}, master_start_time: {log_master_start_time}, master_log_time: {master_log_time}, master_total_run_time: {master_total_run_time}, Raw data: {swarmElement}'
                    logger.info(message)
                    log_only_master = False

def SendDEFINE_SERVER_LOGGER_PACKET(s):
    # print("DEFINE_SERVER_LOGGER_PACKET Sent")
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

	# get IP address
    for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
            #print('%s: %s' % (ifaceName, ', '.join(addresses)))

    # last interface (wlan0) grabbed
    #print(addresses)
    myIP = addresses[0].split('.')
    #print(myIP)
    data= ["" for i in range(8)]

    data[0] = int("F0", 16).to_bytes(1,'little')
    data[1] = int(DEFINE_SERVER_LOGGER_PACKET).to_bytes(1,'little')
    data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    data[4] = int(myIP[0]).to_bytes(1,'little') # 1 octet of ip
    data[5] = int(myIP[1]).to_bytes(1,'little') # 2 octet of ip
    data[6] = int(myIP[2]).to_bytes(1,'little') # 3 octet of ip
    data[7] = int(myIP[3]).to_bytes(1,'little') # 4 octet of ip

    mymessage = ''.encode()  	
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))
	
def SendRESET_SWARM_PACKET(s):
    print("RESET_SWARM_PACKET Sent")
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data= ["" for i in range(8)]

    data[0] = int("F0", 16).to_bytes(1,'little')

    data[1] = int(RESET_SWARM_PACKET).to_bytes(1,'little')
    data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swarm)
    data[3] = int(VERSIONNUMBER).to_bytes(1,'little')
    data[4] = int(0x00).to_bytes(1,'little')
    data[5] = int(0x00).to_bytes(1,'little')
    data[6] = int(0x00).to_bytes(1,'little')
    data[7] = int(0x00).to_bytes(1,'little')
      	
    mymessage = ''.encode()  	
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))

# Getting sensor data log from swarm device
def parseLogPacket(message):

    incomingSwarmID = setAndReturnSwarmID(message[2])
    print("Log From SwarmID:",(message[2]))
	#print("Swarm Software Version:", (message[4]))
	#print("StringLength:",(message[3]))

    logString = ""
    for i in range(0,(message[3])):
        logString = logString + chr((message[i+5]))

	#print("logString:", logString)
    return logString	

def setAndReturnSwarmID(incomingID):
    for i in range(0,SWARMSIZE):
        if (swarmStatus[i][5] == incomingID):
            return i
        else:
            if (swarmStatus[i][5] == 0):  # not in the system, so put it in

                swarmStatus[i][5] = incomingID;
                print("incomingID %d " % incomingID)
                print("assigned #%d" % i)
                return i
            
    # if we get here, then we have a new swarm member.
    # Delete the oldest swarm member and add the new one in
    # (this will probably be the one that dropped out)

    oldTime = time.time();
    oldSwarmID = 0
    for i in range(0,SWARMSIZE):
        if (oldTime > swarmStatus[i][1]):
            ldTime = swarmStatus[i][1]
            oldSwarmID = i
  		
    # remove the old one and put this one in....
    swarmStatus[oldSwarmID][5] = incomingID;
    # the rest will be filled in by Light Packet Receive
    print("oldSwarmID %i" % oldSwarmID)
    return oldSwarmID

# set up sockets for UDP
s=socket(AF_INET, SOCK_DGRAM)
host = 'localhost';
s.bind(('',MYPORT))

print("--------------")
print("LightSwarm Logger")
print("Version ", VERSIONNUMBER)
print("--------------")

#Configuring button and LEDs
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Y_LED, GPIO.OUT)

GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)
signal.signal(signal.SIGINT, signal_handler)

# swarmStatus
# 6 items per swarm item
    # 0 - NP  Not present, P = present, TO = time out
    # 1 - timestamp of last LIGHT_UPDATE_PACKET received
    # 2 - Master or slave status   M S
    # 3 - Current Test Item - 0 - CC 1 - Lux 2 - Red 3 - Green  4 - Blue
    # 4 - Current Test Direction  0 >=   1 <=
    # 5 - IP Address of Swarm

swarmStatus = [[0 for x  in range(6)] for x in range(SWARMSIZE)]

for i in range(0,SWARMSIZE):
    swarmStatus[i][0] = "NP"
    swarmStatus[i][5] = 0

#Used to calculate how long each device has been master
start_time = [0 for i in range(SWARMSIZE)]
current_time = [0 for i in range(SWARMSIZE)]

sensor_data = [[0 for x in range(SWARMSIZE)] for x in range(SWARMSIZE)]

def split_data(data_array):
    x = data_array.split(" | ")
    y = [0 for i in range(len(x))]

    for i in range(len(x)):
        y[i] = x[i].split(",")

    return y

# Read sensor data and update light sensor values to the LED Matrix 
# and swarm ID to the 7 segment display
def get_sensor_values():
    global sensor_data

    sensor_avg_count = 0
    sensor_avg = 0

    while True:

        # Finding average of sensor data received every 1s and plotting every 4s
        sensor_avg += (int(sensor_data[0][3]) / ledMatrix.PLOT_ROW_SIZE)

        sevenSegment.data_7seg = int(sensor_data[0][5])

        if sensor_avg_count == ledMatrix.PLOT_ROW_SIZE:
            matrix_data = ledMatrix.map_sensor_data_to_row(int(sensor_avg))

            if matrix_data != -1:
                ledMatrix.data_mat.append(matrix_data)

            ledMatrix.data_mat = ledMatrix.data_mat[-8:]

            # print("Sensor: ", sensor_avg, "\nData: ", ledMatrix.data_mat)

            sensor_avg = 0
            sensor_avg_count = 0
            
        sensor_avg_count += 1
        time.sleep(1)

# Function that sends and receives sensor data packets
def start_swarm():
    global logFlag, start_time, current_time, sensor_data

    send_server_ip_count = 0
    SendDEFINE_SERVER_LOGGER_PACKET(s)

    while True:

        send_server_ip_count += 1

        # receive datclient (data, addr)
        d = s.recvfrom(1024)

        message = d[0]
        addr = d[1]

        if (len(message) == 8):

            if (message[1] == LIGHT_UPDATE_PACKET):
                incomingSwarmID = setAndReturnSwarmID(message[2])
                swarmStatus[incomingSwarmID][0] = "P"
                swarmStatus[incomingSwarmID][1] = time.time()

                #print("in LIGHT_UPDATE_PACKET")

            if ((message[1]) == RESET_SWARM_PACKET):
                #print("\nSwarm RESET_SWARM_PACKET Received")
                #print("received from addr:",addr)	
                pass

        else:
            if ((message[1]) == LOG_TO_SERVER_PACKET):

                # print("\nSwarm LOG_TO_SERVER_PACKET Received")

                # process the Log Packet
                logString = parseLogPacket(message)
                buildWebMapToFile(logString, SWARMSIZE)
                #Raw data for log file

                sensor_data = split_data(logString)
                # print(sensor_data)

            else:
                print("error message length = ",len(message))

        # Sending server packet to swarm for swarm devices to identify the RPi
        if send_server_ip_count == SEND_SERVER_PACKET:
            SendDEFINE_SERVER_LOGGER_PACKET(s)
            send_server_ip_count = 0

    signal.pause()

def main():
    ledMatrix.setup()
    ledMatrix.matrix_clear()
    sevenSegment.setup()

    t_matrix = threading.Thread(target=ledMatrix.set_LED_matrix)
    t_sensor_data = threading.Thread(target=get_sensor_values)
    t_7segment = threading.Thread(target=sevenSegment.set_7segment)

    t_matrix.start()
    t_sensor_data.start()
    t_7segment.start()

    start_swarm()


if __name__ == "__main__":
	main()