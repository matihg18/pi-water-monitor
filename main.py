import sys
import time
import click
from boya.boya import Boya
from boya.logging.CSVlogger import CSVLogger

# Importaciones de sensores (reales y simulación)
from boya.sensores.sensor_temp import SensorTemp
from boya.sensores.sensor_od import SensorOD
from boya.sensores.sensor_ph import SensorPH
from boya.sensores.sensor_gps import SensorGPS
from boya.sensores.sensor_mock import (
    MockSensorTemp, MockSensorPH, MockSensorOD, MockSensorGPS
)

INTERVALO_MEDICION_SEGUNDOS = 5 
NOMBRE_ARCHIVO_DATOS = "datos_boya.csv"

@click.command()
@click.option('--sim', is_flag=True, help="Ejecuta el sistema con sensores simulados (sin hardware).")
@click.option('--interval', default=INTERVALO_MEDICION_SEGUNDOS, help="Intervalo de medición en segundos.")
def main(sim, interval):
    """Sistema de monitoreo de calidad de agua para Boya UTN-GERU."""
    
    print("\n" + "="*40)
    if sim:
        print("   MODO SIMULACIÓN ACTIVADO (Sin Hardware)")
    else:
        print("   INICIANDO SISTEMA DE BOYA (Hardware Real)")
    print("="*40 + "\n")
    
    # Inicialización del Logger 
    logger = CSVLogger(filename=NOMBRE_ARCHIVO_DATOS)
    
    # Inicialización de los Sensores
    if sim:
        temp_sensor = MockSensorTemp()
        do_sensor = MockSensorOD()
        ph_sensor = MockSensorPH()
        gps_sensor = MockSensorGPS()
    else:
        print("Inicializando sensores de hardware...")
        temp_sensor = SensorTemp()
        do_sensor = SensorOD()
        ph_sensor = SensorPH()
        gps_sensor = SensorGPS(port='/dev/serial0', baudrate=9600) 
    
    print("\n--- Sistema listo para operar ---")

    # Creación del objeto Boya 
    boya_system = Boya(
        temp_sensor=temp_sensor,
        do_sensor=do_sensor,
        ph_sensor=ph_sensor,
        gps_sensor=gps_sensor,
        logger=logger 
    )
    
    # Ejecución del ciclo principal
    try:
        boya_system.run(interval_seg=interval)
    
    except KeyboardInterrupt:
        print("\n\n--- Programa detenido manualmente. Adiós! ---")
        
    except Exception as e:
        print(f"\n\n--- Error irrecuperable en el sistema Boya: {e} ---")
        sys.exit(1)
    
    finally:
        boya_system.close()

if __name__ == "__main__":
    # Asegura que 'boya' sea reconocido como paquete
    if '.' not in sys.path:
        sys.path.append('.') 
        
    main()