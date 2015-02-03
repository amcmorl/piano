#include <avr/io.h>
#include <avr/interrupt.h>

#define PIN_CT 13
#define PIN_RM 10
#define PIN_RI 11
#define PIN_LI 12
#define PIN_LM  9
#define PIN_T1  7
#define PIN_T2  6

int state = 0;
byte out = 0;
int nxt_time = 15624;
int nxt_port = 0;
boolean timeout_okay = true;

union ULInp {
    unsigned long value;
    char bytes[4];
};

void setup() {
  // initialize Timer1
  cli();
  TCCR1A = 0;
  TCCR1B = 0;
  
  // set compare match register to desired timer count
  OCR1A = 15624;
  // turn on the CTC mode
  TCCR1B |= (1 << WGM12);
  // set CS10 and CS12 bits for 1024 prescaler:
  TCCR1B |= (1 << CS10);
  TCCR1B |= (1 << CS12);
  
  // enable Timer1 overflow interrupt:
  TIMSK1 |= (1 << OCIE1A);
  
  // enable global interrupts:
  sei();

  // set output pins
  pinMode(PIN_CT, OUTPUT);
  pinMode(PIN_LM, OUTPUT);
  pinMode(PIN_LI, OUTPUT);
  pinMode(PIN_RI, OUTPUT);
  pinMode(PIN_RM, OUTPUT);
  pinMode(PIN_T1, OUTPUT);
  pinMode(PIN_T2, OUTPUT);
  
  Serial.begin(115200);
}

ISR(TIMER1_COMPA_vect) {
  // put next pin pattern on to digital io pins
    
  // increment buffer index
  // load next timer compare value
  switch (state) {
    case 0:
    case 1:
    // request has been sent, response not received
      if (not timeout_okay) {
        state = 5;
      }
      break;
    case 2:
      PORTD  = (nxt_port >> 8) & B11000000; // set port A for trig pins
      PORTB  = nxt_port & B00111110;        // set port B for LED pins
      TCCR1A = 0;                           // immediately reset timer 
      OCR1A  = nxt_time;                    // set next timeout
      state  = 0;
      timeout_okay = false;
      break;
    }
}

void loop() {
  union ULInp time;
  
  switch (state) {
    case 0:
      // request input
      Serial.write("s0");
      state = 1;
      break;
    case 1:
      // requested entry, waiting for reply
      if (Serial.available() > 0) {
        // always read 5 bytes per cycle
        nxt_port = Serial.read();            // 1
        Serial.readBytes(time.bytes, 4);     // 4
        nxt_time = time.value;
        state = 2;
      }
      break;
    case 5:
      // error
      Serial.write("s5");
      state = 0;
      PORTD = 0;
      PORTB = 0;
      timeout_okay = true;
      break;
  }
}
