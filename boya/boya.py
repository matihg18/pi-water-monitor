import time
from boya.sensores.sensor_temp import SensorTemp
from boya.sensores.sensor_od import SensorOD
from boya.sensores.sensor_ph import SensorPH
from boya.sensores.sensor_gps import SensorGPS
from boya.logging.CSVlogger import CSVLogger

class Boya:
    def __init__(self, temp_sensor: SensorTemp, do_sensor: SensorOD, 
                 ph_sensor: SensorPH, gps_sensor: SensorGPS, logger: CSVLogger):
        
        # Inyección de dependencias (llamadas explícitas)
        self.temp_sensor = temp_sensor
        self.do_sensor = do_sensor
        self.ph_sensor = ph_sensor
        self.gps_sensor = gps_sensor
        self.logger = logger
    

    def run(self, interval_seg=5):

        print(f"\n--- Iniciando Boya - Intervalo de {interval_seg} segundos ---")
        
        while True:
            registro_completo = {'timestamp_local': time.strftime("%Y-%m-%d %H:%M:%S")}
            

            try:
                
                temp_data = self.temp_sensor.read()
                registro_completo.update(temp_data)

                do_data = self.do_sensor.read() 
                registro_completo.update(do_data)
                
                ph_data = self.ph_sensor.read()
                registro_completo.update(ph_data)
                
                gps_data = self.gps_sensor.read()
                registro_completo.update(gps_data)

                self.logger.log(registro_completo)
                
            except Exception as e:
                print(f"ERROR EN EL CICLO DE MEDICIÓN: {e}")

            time.sleep(interval_seg)