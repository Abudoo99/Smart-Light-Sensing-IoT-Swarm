# Smart Light Sensing IoT Swarm 
## Integrating ESP8266 and Raspberry Pi for Data Exchange and Graphical Analysis
## Introduction

A smart light sensing IoT swarm is essential to address the growing demand for intelligent lighting systems that can adapt to various environmental factors and user preferences. These swarms, composed of interconnected Internet of Things (IoT) devices equipped with light sensors, offer several advantages. Firstly, they enhance energy efficiency by autonomously adjusting the illumination levels based on natural light availability, thereby reducing energy consumption. Additionally, the swarm's collective intelligence enables the synchronization of lighting across spaces, optimizing overall illumination and creating a seamless user experience.

Furthermore, smart light sensing IoT swarms contribute to environmental sustainability by minimizing light pollution, ensuring that artificial lighting aligns with real-time requirements. This capability is particularly crucial in urban areas where excess artificial light can disrupt ecosystems and affect human well-being. Moreover, the adaptive nature of these swarms caters to user comfort and productivity, as they can dynamically respond to changes in occupancy, preferences, and specific tasks.

## Hardware Specifications

1. Raspberry Pi Model 4 <br><br>
<img src="https://github.com/Abudoo99/smart-light-sensing-iot-swarm/assets/69448986/78f589c8-9e7c-41a6-ac35-2ca4f48cfb4a" width="100" height="100" ><br>
2. ESP8266 <br><br>
<img src="https://github.com/Abudoo99/smart-light-sensing-iot-swarm/assets/69448986/115532b1-bf1f-401e-9764-ed0f8848ae98" width="100" height="100" ><br>
3. 4-digit 7 Segment Display <br><br>
<img src="https://github.com/Abudoo99/smart-light-sensing-iot-swarm/assets/69448986/31373592-2aa8-41d4-a9ca-0c41439646e7" width="100" height="100" ><br>
4. 8x8 LED Matrix <br><br>
<img src="https://github.com/Abudoo99/smart-light-sensing-iot-swarm/assets/69448986/6ad57af3-4277-4eef-942e-829607bb2ac0" width="200" height="100" ><br>
5. 74HC595 Serial Shifter (For LED Matrix and 7 segment display) <br><br>
<img src="https://github.com/Abudoo99/smart-light-sensing-iot-swarm/assets/69448986/bc422c18-7b1f-452e-a89a-fbc129cf22da" width="100" height="100" ><br>
6. Circular LED <br><br>
<img src="https://github.com/Abudoo99/smart-light-sensing-iot-swarm/assets/69448986/44edf0c5-8363-4987-a97f-76f2141fa48a" width="100" height="100" ><br>

## Wiring Schematic and Overview
<img src="https://github.com/Abudoo99/smart-light-sensing-iot-swarm/assets/69448986/085dc22a-ced0-4fab-a3de-b8011d67de0a" width="500" height="500" ><br>
*	The connections are made as per the above wiring schematic. A photoresistor is connected to each ESP8266 device. The sensor value is indicated with the pattern on the circular LED.
*	Initially, there is no communication between the devices.
*	First, an ESP8266 device connects to the swarm and sends light update packets into the swarm once the sensor value is obtained. 
*	Then, the RPi joins the swarm. It sends server information into the swarm and receives logs sent from other devices in the swarm.
*	Each ESP device sends their light sensor value into the swarm. The device that has the highest sensor value becomes the master and sends the light sensor data to the RPi.
*	When the push button is pressed in the Pi, the Pi sends a RESET swarm packet to the swarm and glows the yellow LED for 3s and creates a log file to store the sensor values and other information.

## Raspberry Pi Setup and Packet Delivery Flow
<img src="https://github.com/Abudoo99/smart-light-sensing-iot-swarm/assets/69448986/f0825c06-ed06-4e15-b09f-8e16b4200cff" width="500" height="500" ><br>

## ESP8266 Setup and Packet Delivery Flow
<img src="https://github.com/Abudoo99/smart-light-sensing-iot-swarm/assets/69448986/4041550b-1128-425a-abe2-a067f6cf0c9c" width="500" height="700" ><br>

## Limitations
* While UDP offers low-latency communication, its limitations in terms of reliability, security and congestion control needs to be addressed carefully
* As the number of devices increase, the complexity and power consumption of the system increases
* Expanding the swarm to cover larger areas (Scalability)

