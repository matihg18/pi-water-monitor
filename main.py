import sys
import time
from boya.boya import Boya
from boya.sensores.sensor_temp import SensorTemp
from boya.sensores.sensor_od import SensorOD
from boya.sensores.sensor_ph import SensorPH
from boya.sensores.sensor_gps import SensorGPS
from boya.logging.CSVlogger import CSVLogger



INTERVALO_MEDICION_SEGUNDOS = 5 
NOMBRE_ARCHIVO_DATOS = "datos_boya.csv"

def main():

    print("Iniciando sistema de Boya...")
    
    #Inicialización del Logger 
    logger = CSVLogger(filename=NOMBRE_ARCHIVO_DATOS)
    
    #Inicialización de los Sensores
    print("Inicializando sensores...")

    temp_sensor = SensorTemp()
    do_sensor = SensorOD()
    ph_sensor = SensorPH()
    gps_sensor = SensorGPS(port='/dev/serial0', baudrate=9600) 
    
    print("\n--- Sensores listos (Verifique mensajes de error arriba) ---")

    #Creación del objeto Boya 
    boya_system = Boya(
        temp_sensor=temp_sensor,
        do_sensor=do_sensor,
        ph_sensor=ph_sensor,
        gps_sensor=gps_sensor,
        logger=logger 
    )
    
    #Ejecución del ciclo principal
    try:
        boya_system.run(interval_seg=INTERVALO_MEDICION_SEGUNDOS)
    
    except KeyboardInterrupt:
        print("\n\n--- Programa detenido manualmente. Adiós! ---")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n\n--- Error irrecuperable en el sistema Boya: {e} ---")
        sys.exit(1)

if __name__ == "__main__":
    # Esta línea asegura que el sistema sepa que 'boya' es el paquete raíz
    # (Necesario para las importaciones si ejecutas desde la carpeta del proyecto)
    if '.' not in sys.path:
        sys.path.append('.') 
        
    main()