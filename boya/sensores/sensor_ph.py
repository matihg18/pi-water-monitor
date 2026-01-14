import time
from boya.sensores.isensor import ISensor
from boya.lib.AtlasI2C import AtlasI2C 

class SensorPH(ISensor):
    PH_ADDRESS = 99 

    def __init__(self):
        try:
            self.ph_sensor = AtlasI2C(address=self.PH_ADDRESS, moduletype="pH")
            print(f"Sensor pH inicializado en I2C, dirección {self.PH_ADDRESS}")
        except Exception as e:
            print(f"Error al inicializar pH Sensor: {e}")
            self.ph_sensor = None

    def read(self) -> dict:
        if self.ph_sensor is None:
             return {"error_ph": "pH sensor no conectado"}

        try:
            response_full = self.ph_sensor.query("R")

            if response_full.startswith("Success"):
                value_str = response_full.split(": ")[-1].strip()
                ph_value = float(value_str)
                return {"ph_value": ph_value}
            else:
                return {"error_ph_status": response_full}

        except Exception as e:
            return {"ph_value": None, "error_ph": str(e)}