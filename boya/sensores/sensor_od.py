import time
from boya.sensores.isensor import ISensor
from boya.lib.AtlasI2C import AtlasI2C


class SensorOD(ISensor):
    DO_ADDRESS = 97

    def __init__(self):
        try:
            self.do_sensor = AtlasI2C(address=self.DO_ADDRESS, moduletype="DO")
            print(f"Sensor DO inicializado en I2C, dirección {self.DO_ADDRESS}")
        except Exception as e:
            print(f"Error al inicializar DO Sensor: {e}")
            self.do_sensor = None

    def read(self, temp_c_value=None) -> dict:
        if self.do_sensor is None:
             return {"error_do": "DO sensor no conectado"}

        try:
            temp_default = 20.0 
            temp_to_use = temp_c_value if temp_c_value is not None else temp_default
            
            self.do_sensor.write(f"T,{temp_to_use}") 
            time.sleep(self.do_sensor.short_timeout) 

            #LECTURA PRINCIPAL
            response_full = self.do_sensor.query("R")
            
            if response_full.startswith("Success"):
                value_str = response_full.split(": ")[-1].strip()
                do_value = float(value_str)
                return {"oxigeno_disuelto_mgL": do_value}
            else:
                return {"error_do_status": response_full}

        except Exception as e:
            return {"oxigeno_disuelto_mgL": None, "error_od": str(e)}
