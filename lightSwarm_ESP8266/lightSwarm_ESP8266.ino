/*  Smart Light Sensing IoT Swarm 
*     Author  : Abyukth Kumar
*/

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <Adafruit_NeoPixel.h>

//#define DEBUG

char ssid[] = "********";            //  your network SSID (name)
char pass[] = "********";       // your network password

#define VERSIONNUMBER   29
#define SWARMSIZE       6

#define MAX_BROADCAST_DELAY   50

// Ring LED configurations
#define LED_PIN     D1
#define NUM_PIXELS  8

Adafruit_NeoPixel pixels(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

// 30 seconds is too old - it must be dead
#define SWARMTOOOLD 30000

int mySwarmID = 0;
int incomingSwarmID;

// Packet Types
#define LIGHT_UPDATE_PACKET 0
#define RESET_SWARM_PACKET 1
#define DEFINE_SERVER_LOGGER_PACKET 2
#define LOG_TO_SERVER_PACKET 3


unsigned int localPort = 1999;      // local port to listen for UDP packets

boolean masterState = true;   // True if master, False if slave

int swarmLightData[SWARMSIZE];
int swarmVersion[SWARMSIZE];
int swarmState[SWARMSIZE];
long swarmTimeStamp[SWARMSIZE];   // for aging

IPAddress serverAddress = IPAddress(0, 0, 0, 0); // default no IP Address

int swarmAddresses[SWARMSIZE];  // Swarm addresses

// variables for light sensor
 int i, sensor_value = 0;

const int PACKET_SIZE = 8; // Light Update Packet
const int BUFFERSIZE = 1024;

byte packetBuffer[BUFFERSIZE]; //buffer to hold incoming and outgoing packets

// A UDP instance to let us send and receive packets over UDP
WiFiUDP udp;

IPAddress localIP;

void setup()
{
  Serial.begin(9600);

  //Configuring onboard and external LEDs (initially turned OFF)
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); 

  //Configuring photoresistor light sensor
  pinMode(A0, INPUT);

  //Configuring Ring LED
  pixels.begin();
  pixels.setBrightness(100);

  //Connecting to WiFi network
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("");

  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  //UDP setup
  Serial.println("Starting UDP");
  udp.begin(localPort);
  Serial.print("Local port: ");
  Serial.println(udp.localPort());


  // initialize light sensor and arrays
  for (i = 0; i < SWARMSIZE; i++)
  {
    swarmAddresses[i] = 0;
    swarmLightData[i] = 0;
    swarmTimeStamp[i] = -1;
  }
  swarmLightData[mySwarmID] = 0;
  swarmTimeStamp[mySwarmID] = 1;   // I am always in time to myself
  swarmVersion[mySwarmID] = VERSIONNUMBER;
  swarmState[mySwarmID] = masterState;
  Serial.print("Sensor_value =");
  Serial.println(sensor_value);


  //Set SwarmID based on IP address 
  localIP = WiFi.localIP();
  swarmAddresses[0] =  localIP[3];
  
  //Initial Swarm ID
  mySwarmID = 0;
  Serial.print("My LightSwarm Instance: ");
  Serial.println(mySwarmID);
}

void loop()
{
  int led_brightness;

  //Get photoresistor light sensor value   
  sensor_value = analogRead(A0);
  Serial.printf("Sensor Data: %d\n", sensor_value);
  swarmLightData[mySwarmID] = sensor_value;

  //Using Ring LED to represent sensor values
  displayPatternLED(sensor_value);

  int cb = udp.parsePacket();
  if (!cb) 
  {
    //  Serial.println("no packet yet");
  }
  else
  {
    //Read received packet into the buffer
    udp.read(packetBuffer, PACKET_SIZE); 

#ifdef DEBUG
    Serial.print("packetbuffer[1] =");
    Serial.println(packetBuffer[1]);
#endif

    if (packetBuffer[1] == LIGHT_UPDATE_PACKET)
    {
      Serial.print("LIGHT_UPDATE_PACKET received from LightSwarm #");
      Serial.println(packetBuffer[2]);

      //Assign ID for the incoming swarm device
      incomingSwarmID = setAndReturnMySwarmIndex(packetBuffer[2]);
      
#ifdef DEBUG
      Serial.printf("\tIncoming Swarm ID : %d\n", incomingSwarmID);
      Serial.print("\tLS Packet Received from #");
      Serial.print(packetBuffer[2]);

      Serial.print("\tSwarmState:");
      if (packetBuffer[3] == 0)
        Serial.println("SLAVE");
      else
        Serial.println("MASTER");
      
      Serial.print("\tSensor Value:");
      Serial.print(packetBuffer[5] * 256 + packetBuffer[6]);
      Serial.print("\tVersion=");
      Serial.println(packetBuffer[4]);
#endif

      //Record the incoming packet into the swarm array
      swarmLightData[incomingSwarmID] = packetBuffer[5] * 256 + packetBuffer[6];
      swarmVersion[incomingSwarmID] = packetBuffer[4];
      swarmState[incomingSwarmID] = packetBuffer[3];
      swarmTimeStamp[incomingSwarmID] = millis();

      //Check to see if our swarm device is a master device
      checkAndSetIfMaster();
    }

    if (packetBuffer[1] == RESET_SWARM_PACKET)
    {
      Serial.println(">>>>>>>>>RESET_SWARM_PACKETPacket Received");
      masterState = true;
      Serial.println("Reset Swarm:  I just BECAME Master (and everybody else!)");
      digitalWrite(LED_BUILTIN, LOW);
      delay(3000);  //To visualize that the packet has been received
    }
  }

  if (packetBuffer[1] ==  DEFINE_SERVER_LOGGER_PACKET)
  {
    Serial.println(">>>>>>>>>DEFINE_SERVER_LOGGER_PACKET Packet Received");
    serverAddress = IPAddress(packetBuffer[4], packetBuffer[5], packetBuffer[6], packetBuffer[7]);
    Serial.print("Server address received: ");
    Serial.println(serverAddress);
  }

  Serial.print("\nDevice State: ");
  if (masterState == true)
  {
    digitalWrite(LED_BUILTIN, LOW);
    Serial.print("MASTER");
  }
  else
  {
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.print("SLAVE");
  }
  Serial.print(" / Sensor Reading: ");
  Serial.print(sensor_value);
  Serial.print(" / Server Address: ");
  Serial.println(serverAddress);
  Serial.println("----------------------");

  for (i = 0; i < SWARMSIZE; i++)
  {
    Serial.print("swarmAddress[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.println(swarmAddresses[i]); 
  }
  Serial.println("----------------------");

  //Broadcasting light update packet
  broadcastARandomUpdatePacket();

  //Sending sensor data log to server
  sendLogToServer();

}

// Send a LIGHT Packet request to the swarms at the given address
void sendLightUpdatePacket(IPAddress & address)
{
#ifdef DEBUG
  Serial.print("Sending Light Update packet to ");
  Serial.println(address);
#endif

  //Initializing packet buffer
  memset(packetBuffer, 0, PACKET_SIZE);

  //Initialize values needed to form Light Packet
  packetBuffer[0] = 0xF0;   // StartByte
  packetBuffer[1] = LIGHT_UPDATE_PACKET;     // Packet Type
  packetBuffer[2] = localIP[3];     // Sending Swarm Number
  packetBuffer[3] = masterState;  // 0 = slave, 1 = master
  packetBuffer[4] = VERSIONNUMBER;  // Software Version
  packetBuffer[5] = (sensor_value & 0xFF00) >> 8; // Clear High Byte
  packetBuffer[6] = (sensor_value & 0x00FF); // Clear Low Byte
  packetBuffer[7] = 0x0F;  //End Byte

  //Sending packets using UDP
  udp.beginPacketMulticast(address, localPort, WiFi.localIP()); 
  //udp.beginPacket(address, localPort); 
  udp.write(packetBuffer, PACKET_SIZE);
  udp.endPacket();
}

// Broadcast light update packets into the swarm at random delays
void broadcastARandomUpdatePacket()
{
  int sendToLightSwarm = 255, randomDelay;

  Serial.print("Broadcast ToSwarm = ");
  Serial.print(sendToLightSwarm);
  Serial.print(" | ");

  Serial.print("Delay = ");
  randomSeed(swarmAddresses[0]);
  randomDelay = random(0, MAX_BROADCAST_DELAY);
  Serial.print(randomDelay);
  Serial.print("ms |");

  delay(randomDelay);

  IPAddress sendSwarmAddress(192, 168, 0, sendToLightSwarm); // my Swarm Address
  sendLightUpdatePacket(sendSwarmAddress);
}

// Checking if our device is the master
void checkAndSetIfMaster()
{
  int i;
  for (i = 0; i < SWARMSIZE; i++)
  {

#ifdef DEBUG
    Serial.print("swarmLightData[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.print(swarmLightData[i]);
    Serial.print("\tswarmTimeStamp[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.println(swarmTimeStamp[i]);
#endif

    //Check if device is present in the swarm
    int howLongAgo = millis() - swarmTimeStamp[i] ;

    if (swarmTimeStamp[i] == 0)
    {
      //Serial.println(" TO");  //Timeout
    }
    else if (swarmTimeStamp[i] == -1)
    {
      //Serial.println(" NP");  //Not present
    }
    else if (swarmTimeStamp[i] == 1)
    {
      //Serial.println(" ME");  //Our device
    }
    else if (howLongAgo > SWARMTOOOLD)
    {
      //Serial.println(" TO");  //Timeout
      swarmTimeStamp[i] = 0;
      swarmLightData[i] = 0;

    }
    else
    {
      //Serial.println(" PR");  //Present
    }
  }
  Serial.println();
  
  boolean setMaster = true;

  //Checking if any other device in the swarm has a higher sensor value
  for (i = 0; i < SWARMSIZE; i++)
  {
    if (swarmLightData[mySwarmID] >= swarmLightData[i])
    {
      // I might be master :D
    }
    else
    {
      //Not master :(
      setMaster = false;
      break;
    }
  }

  //If we become master, this segment is executed
  if (setMaster == true)
  {
    if (masterState == false)
    {
      Serial.println("I just BECAME Master");
    }
    masterState = true;
  }
  else
  {
    if (masterState == true)
    {
      Serial.println("I just LOST Master");
    }    
    masterState = false;
  }

  //Storing our swarm device state
  swarmState[mySwarmID] = masterState;

}

int setAndReturnMySwarmIndex(int incomingID)
{
  for (i = 0; i< SWARMSIZE; i++)
  {
    if (swarmAddresses[i] == incomingID)
    {
       return i;
    } 
    else if (swarmAddresses[i] == 0)  // not in the system, so put it in
    {
      swarmAddresses[i] = incomingID;
      Serial.print("incomingID ");
      Serial.print(incomingID);
      Serial.print("  assigned #");
      Serial.println(i);
      return i;
    }
  }  
  
  // if we get here, then we have a new swarm member.   
  // Delete the oldest swarm member and add the new one in 
  // (this will probably be the one that dropped out)
  
  int oldSwarmID;
  long oldTime;
  oldTime = millis();
  for (i = 0;  i < SWARMSIZE; i++)
  {
    if (oldTime > swarmTimeStamp[i])
    {
      oldTime = swarmTimeStamp[i];
      oldSwarmID = i;
    }
  } 
 
  // remove the old one and put this one in....
  swarmAddresses[oldSwarmID] = incomingID;
  
  return 0;
}


// Send log packet to Server if master and server address defined
void sendLogToServer()
{
  char myBuildString[1000];
  myBuildString[0] = '\0';

  if (masterState == true)
  {
    //Check if server address is available in the swarm
    if ((serverAddress[0] == 0) && (serverAddress[1] == 0))
    {
      return;
    }
    else
    {
      // Sending packet as a string in the following format:
      // swarmID, MasterSlave, SoftwareVersion, sensor_value, Status | ....next Swarm ID
      // 0,1,15,3883, PR | 1,0,14,399, PR | ....

      int i;
      char swarmString[20];
      swarmString[0] = '\0';

      for (i = 0; i < SWARMSIZE; i++)
      {

        char stateString[5];
        stateString[0] = '\0';
        if (swarmTimeStamp[i] == 0)
        {
          strcat(stateString, "TO");
        }
        else if (swarmTimeStamp[i] == -1)
        {
          strcat(stateString, "NP");
        }
        else if (swarmTimeStamp[i] == 1)
        {
          strcat(stateString, "PR");
        }
        else
        {
          strcat(stateString, "PR");
        }

        sprintf(swarmString, " %i,%i,%i,%i,%s,%i ", i, swarmState[i], swarmVersion[i], swarmLightData[i], stateString, swarmAddresses[i]);

        strcat(myBuildString, swarmString);
        if (i < SWARMSIZE - 1)
        {
          strcat(myBuildString, "|");
        }
      }
    }

    // set all bytes in the buffer to 0
    memset(packetBuffer, 0, BUFFERSIZE);
    // Initialize values needed to form Light Packet
    packetBuffer[0] = 0xF0;   // StartByte
    packetBuffer[1] = LOG_TO_SERVER_PACKET;     // Packet Type
    packetBuffer[2] = localIP[3];     // Sending Swarm Number
    packetBuffer[3] = strlen(myBuildString); // length of string in bytes
    packetBuffer[4] = VERSIONNUMBER;  // Software Version

    for (i = 0; i < strlen(myBuildString); i++)
    {
      packetBuffer[i + 5] = myBuildString[i];// first string byte
    }

    packetBuffer[i + 5] = 0x0F; //End Byte
    Serial.print("Sending Log to Server:");
    Serial.println(myBuildString);
    int packetLength;
    packetLength = i + 5 + 1;

    udp.beginPacket(serverAddress,  localPort); 

    udp.write(packetBuffer, packetLength);
    udp.endPacket();
  }
}

void displayPatternLED(int sensor_value)
{
  pixels.clear();

  //GREEN to indicate low sensor value
  if((sensor_value > 0)&&(sensor_value < 500))
  {
    if((sensor_value > 0)&&(sensor_value < 300))
    {
      pixels.setPixelColor(0, pixels.Color(0, 150, 0));
    }
    if((sensor_value >= 300)&&(sensor_value < 400))
    {
      pixels.setPixelColor(0, pixels.Color(0, 150, 0));
      pixels.setPixelColor(1, pixels.Color(0, 150, 0));
    }
    if((sensor_value >= 400)&&(sensor_value < 500))
    {
      pixels.setPixelColor(0, pixels.Color(0, 150, 0));
      pixels.setPixelColor(1, pixels.Color(0, 150, 0));
      pixels.setPixelColor(2, pixels.Color(0, 150, 0));
    }
  }

  //ORANGE to indicate moderate sensor value
  else if((sensor_value >= 500)&&(sensor_value < 800))
  {
    if((sensor_value >= 500)&&(sensor_value < 600))
    {  
      pixels.setPixelColor(0, pixels.Color(255, 75, 0));
      pixels.setPixelColor(1, pixels.Color(255, 75, 0));
      pixels.setPixelColor(2, pixels.Color(255, 75, 0));
      pixels.setPixelColor(3, pixels.Color(255, 75, 0));
    }
    if((sensor_value >= 600)&&(sensor_value < 700))
    {
      pixels.setPixelColor(0, pixels.Color(255, 75, 0));
      pixels.setPixelColor(1, pixels.Color(255, 75, 0));
      pixels.setPixelColor(2, pixels.Color(255, 75, 0));
      pixels.setPixelColor(3, pixels.Color(255, 75, 0));
      pixels.setPixelColor(4, pixels.Color(255, 75, 0));
    }
    if((sensor_value >= 700)&&(sensor_value < 800))
    {
      pixels.setPixelColor(0, pixels.Color(255, 75, 0));
      pixels.setPixelColor(1, pixels.Color(255, 75, 0));
      pixels.setPixelColor(2, pixels.Color(255, 75, 0));
      pixels.setPixelColor(3, pixels.Color(255, 75, 0));
      pixels.setPixelColor(4, pixels.Color(255, 75, 0));
      pixels.setPixelColor(5, pixels.Color(255, 75, 0));
    }
  }

  //RED to indicate high sensor reading
  else if(sensor_value >= 800)
  {
    if((sensor_value >= 800)&&(sensor_value < 900))
    {
      pixels.setPixelColor(0, pixels.Color(255, 0, 0));
      pixels.setPixelColor(1, pixels.Color(255, 0, 0));
      pixels.setPixelColor(2, pixels.Color(255, 0, 0));
      pixels.setPixelColor(3, pixels.Color(255, 0, 0));
      pixels.setPixelColor(4, pixels.Color(255, 0, 0));
      pixels.setPixelColor(5, pixels.Color(255, 0, 0));
      pixels.setPixelColor(6, pixels.Color(255, 0, 0));      
    }
    if((sensor_value >= 900))
    { 
      pixels.setPixelColor(0, pixels.Color(255, 0, 0));
      pixels.setPixelColor(1, pixels.Color(255, 0, 0));
      pixels.setPixelColor(2, pixels.Color(255, 0, 0));
      pixels.setPixelColor(3, pixels.Color(255, 0, 0));
      pixels.setPixelColor(4, pixels.Color(255, 0, 0));
      pixels.setPixelColor(5, pixels.Color(255, 0, 0));
      pixels.setPixelColor(6, pixels.Color(255, 0, 0));
      pixels.setPixelColor(7, pixels.Color(255, 0, 0));
    }
  } 

  //Display pattern
  pixels.show();
}

