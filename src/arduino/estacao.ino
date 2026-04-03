// Definição dos pinos analógicos
const int pinoTemp = A0;      // TMP36
const int pinoUmidade = A1;   // Sensor de Solo
const int pinoPressao = A2;   // Potenciômetro

void setup() {
  Serial.begin(9600); // Inicializa a comunicação serial [cite: 85]
}

void loop() {
  // 1. Leitura e Conversão da Temperatura (TMP36)
  int leituraTemp = analogRead(pinoTemp);
  float voltagem = leituraTemp * (5.0 / 1024.0);
  float temp = (voltagem - 0.5) * 100.0; // Conversão para Celsius

  // 2. Leitura e Mapeamento da Umidade (0 a 100%)
  int leituraUmid = analogRead(pinoUmidade);
  float umid = map(leituraUmid, 0, 1023, 0, 100);

  // 3. Leitura e Mapeamento da Pressão (opcional, simulando 950 a 1050 hPa)
  int leituraPres = analogRead(pinoPressao);
  float pressao = map(leituraPres, 0, 1023, 950, 1050);

  // 4. Envio dos dados via Serial em formato JSON 
  Serial.print("{");
  Serial.print("\"temperatura\":"); Serial.print(temp);
  Serial.print(",\"umidade\":"); Serial.print(umid);
  Serial.print(",\"pressao\":"); Serial.print(pressao);
  Serial.println("}");

  // Intervalo de 5 segundos conforme requisito [cite: 96]
  delay(5000);
}