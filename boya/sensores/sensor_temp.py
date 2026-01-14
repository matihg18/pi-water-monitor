from w1thermsensor import W1ThermSensor, NoSensorFoundError
from boya.sensores.isensor import ISensor

class SensorTemp(ISensor):
    def __init__(self):
        try:
            self.sensor = W1ThermSensor()
            print("Sensor de Temperatura DS18B20 inicializado (1-Wire)")
        except NoSensorFoundError:
            print("Error: Sensor DS18B20 no encontrado. Verifica la conexión 1-Wire.")
            self.sensor = None
        except Exception as e:
            print(f"Error general al inicializar DS18B20: {e}")
            self.sensor = None

    def read(self) -> dict:
        if self.sensor is None:
            return {"error_temp": "Sensor de temperatura no disponible"}

        try:
            temperatura_c = self.sensor.get_temperature()
            
            return {"temperatura_ambiente_C": temperatura_c}
            
        except Exception as e:
            return {"error_temp_reading": str(e)}