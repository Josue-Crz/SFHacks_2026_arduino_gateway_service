// SFHacks 2026 GreenSense Prototype
// Prototype of GreenSense device using Arduino libraries

// WIP
// libraries & their purpose

// DHT11 Library
#include <dht_nonblocking.h>
#define DHT_SENSOR_TYPE DHT_TYPE_11

// Global Variables, related to the wire diagram of the device
// Pin Macros preprocessor definitions(split up by each subdevice)


// DHT_Sensor :
static const int DHT_SENSOR_PIN = 2;
DHT_nonblocking dht_sensor( DHT_SENSOR_PIN, DHT_SENSOR_TYPE );


// LCD Display :
#include <LiquidCrystal.h>
// init LCD lib via pins
LiquidCrystal lcd(4, 7, 3, 5, 6, 8);
#define LCDDelay 2000



// 74HC595N eight led setup
const int clockPin = 10;
const int latchPin = 11;
const int dataPin = 12;
const int LEDdelay = 100; // 100 milliseconds to allow registers to shift within 74HC5959N

// 74HC595N BYTE VARIABLE TO DETERMINE what LED value will light up within 8 bit register
byte ledLightPosition = 0;


// joystick button control
const int SW_pin = 13;
int joyStickPressState = 0;









void setup() // initialize macro digital pins
{
    Serial.begin(2000000); // purpose: have extremely fast real time data sent from arduino to parsed information, updated in real time


    // lcd setup
    lcd.begin(16,2);

    // 74HC595N setup
    pinMode(latchPin, OUTPUT);
    pinMode(dataPin, OUTPUT);
    pinMode(clockPin, OUTPUT);

    //joystick part setup
    pinMode(SW_pin, INPUT);
    digitalWrite(SW_pin, HIGH);
}




// METHODS PROVIDED FROM Arduino
// Author: Arduino 1.8.19

// 74HC595N update lights method provided -> updateShiftRegister
void updateShiftRegister() // if it doesnt work may have to set as static
{
   digitalWrite(latchPin, LOW);
   shiftOut(dataPin, clockPin, LSBFIRST, ledLightPosition);
   digitalWrite(latchPin, HIGH);
}



//DHT11 sensor provided method
static bool measure_environment( float *temperature, float *humidity )
{
  static unsigned long measurement_timestamp = millis( );

  /* Measure once every four seconds. */
  if( millis( ) - measurement_timestamp > 3000ul )
  {
    if( dht_sensor.measure( temperature, humidity ) == true )
    {
      measurement_timestamp = millis( );
      return( true );
    }
  }

  return( false );
}

// ------------------------------------------------------------



void loop()
{
    float temperature;
    float humidity;

    // grab data
    // parse humidity & temp info
    if( measure_environment( &temperature, &humidity ) == true )
      {
          
        
          Serial.print("T=");
          Serial.println(temperature, 1);

          Serial.print("Humidity=");
          Serial.println(humidity, 1);
          //delay(1000); // issue was it wasn't allowing data to be parsed it was too fast
      }


      // output data onto the LCD


   // USER must keep button held down to see humidity
   // check if user made input for changing display
  
      // allow user to see what was outputted of previously task for a little more
      delay(LCDDelay);
      lcd.clear();

      // CHANGE DISPLAY
      lcd.setCursor(0,0);
      lcd.print("Humidity:");
      lcd.print(humidity, 1);
   
        

        // C (prior to this temperature was being measured to fahrenheit) -> F
        temperature = (temperature * 9) / 5 + 32;

        
        // CHANGE DISPLAY
        lcd.setCursor(0,0);
        lcd.print("Temp.:");
        lcd.print(temperature, 1);
        lcd.print("F");
        
   



   // FIXME THE GREENSCORE INDICATOR TO BE DISPLAYED TO USER
   // now calculate based off temperature and humidity greenscore index -> determine LED lights
   // change light of 8 LEDs
   int greenScore = temperature + humidity; // FIXME! will be calculated based off previous temp and humidity

   // DUMMY VARIABLE DELETE LATER -> EXPECT YELLOW LIGHT
   greenScore = humidity; 

   // wanted to implement a point system


   // BRANCH STATEMENTS OFF greenscore index
   // if-elif-else below

   if(greenScore > 80){ // green led branch
        // light up only green leds
        ledLightPosition = B00000011;
   }

   else if(greenScore <= 80 && greenScore > 60){ // yellow led branch
        // light up only yellow leds
        ledLightPosition = B00001100;
   }
   else if(greenScore <= 60 && greenScore > 40){ // blue led branch
        // light up only orange leds
        ledLightPosition = B00110000;
   }
   else{ // red led branch
        // light up only red leds
        ledLightPosition = B11000000;
   }

   // once LED vars are set shift binary data in 74FC595 to respective branch
   updateShiftRegister();

   // ---------------------------

   // USER INPUT BELOW PHYSICALLY

   // JOYBUTTONPRESS

   //joyStickPressState = digitalRead(SW_pin); // exepected return type: 0(LOW -> for temperature), 1(HIGH -> for humidity (brief period)

        //delay(500); // extra delay for safety measure of time constraint, often an action for proper electronic workings
}
