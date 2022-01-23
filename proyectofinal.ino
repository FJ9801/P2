int Velocidades[] = {0,0,0,0};
int izquierda = 3;
int derecha = 9;
int paletas = 5;
int conveyor = 6;
int izq1 = 2;
int izq2 = 4;
int der1 = 7;
int der2 = 8;
int x = 0;

void setup() {
  // initialize both serial ports:
  pinMode(izquierda,OUTPUT);
  pinMode(derecha,OUTPUT);
  pinMode(paletas,OUTPUT);
  pinMode(conveyor,OUTPUT);
  pinMode(izq1,OUTPUT);
  pinMode(izq2,OUTPUT);
  pinMode(der1,OUTPUT);
  pinMode(der2,OUTPUT);
  Serial.begin(9600);
 }

void loop() {

   String incoming;
  //digitalWrite(led, LOW);
  if (Serial.available()) {
     x = 0;
      incoming = Serial.readStringUntil('\n');
      
      String s = "";
  
      for (int i = 0, j = 0; i < incoming.length(); ++i) {
        if (incoming[i] == ',' || i == incoming.length()-1) {
          if (i == incoming.length()-1){
            s += incoming[i];
          }
          Velocidades[j] = s.toInt();
          s = "";
          ++j;
          continue;
        }
        
        s += incoming[i];
        
      }
  }
 
  
        if(Velocidades[0] >= 0){
          analogWrite(izquierda, Velocidades[0]);
          digitalWrite(izq1, true);
          digitalWrite(izq2, false);
          }
        
        else{
          analogWrite(izquierda, -1*Velocidades[0]);
          digitalWrite(izq1, false);
          digitalWrite(izq2, true);
          }
        
        if(Velocidades[1] >= 0){
          analogWrite(derecha, Velocidades[1]);
          digitalWrite(der1, true);
          digitalWrite(der2, false);
          } 
        
        else{
          analogWrite(derecha, -1*Velocidades[1]);
          digitalWrite(der1, false);
          digitalWrite(der2, true);
          }
          
        analogWrite(paletas, Velocidades[2]);
        analogWrite(conveyor, Velocidades[3]);

        ++x;
        if(x == 50000){
          Velocidades[0] = 0;
          Velocidades[1] = 0;
          Velocidades[2] = 0;
          Velocidades[3] = 0;
        }
}
