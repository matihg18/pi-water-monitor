import serial
import pynmea2
from boya.sensores.isensor import ISensor

class SensorGPS(ISensor):
    def __init__(self,port='/dev/serial0',baudrate=9600):
        try:
            self.serial_conn = serial.Serial(port, baudrate, timeout=1)
            print(f"GPS conectado en {port}")
        except Exception as e:
            print(f"Error al conectar GPS: {e}")
            self.serial_conn = None

        self.last_data = {
            "latitud": None,
            "longitud": None,
            "altitud_ft": 0.0,
            "rumbo_deg": 0.0,
            "velocidad_mph": 0.0,
            "satelites": 0,
            "gps_status": "Iniciando"
        }

    def read(self) -> dict:
        if self.serial_conn is None:
            return {"gps_status": "Error Hardware"}

        try:
            # Leemos un bloque de líneas para asegurarnos de capturar RMC y GGA
            # El buffer suele tener varias sentencias acumuladas
            lines_to_read = 15 
            
            for _ in range(lines_to_read):
                if self.serial_conn.in_waiting == 0:
                    break
                    
                line = self.serial_conn.readline().decode('ascii', errors='replace').strip()
                
                try:
                    if line.startswith('$'):
                        msg = pynmea2.parse(line)
                        
                        # --- 1. Procesar GPRMC (Recomendado para: Vel, Rumbo, Posición) ---
                        if isinstance(msg, pynmea2.types.talker.RMC):
                            if msg.status == 'A': 
                                self.last_data["latitud"] = float(msg.latitude)
                                self.last_data["longitud"] = float(msg.longitude)
                                self.last_data["gps_status"] = "Fix OK"
                                
                                if msg.spd_over_grnd:
                                    self.last_data["velocidad_mph"] = float(msg.spd_over_grnd) * 1.852
                                
                                if msg.true_course:
                                    self.last_data["rumbo_deg"] = float(msg.true_course)

                        # --- 2. Procesar GPGGA (Necesario para: Altitud, Satélites) ---
                        elif isinstance(msg, pynmea2.types.talker.GGA):
                            if msg.quality > 0: # 0 = Inválido, 1/2 = GPS Fix
                                self.last_data["latitud"] = float(msg.latitude)
                                self.last_data["longitud"] = float(msg.longitude)
                                self.last_data["gps_status"] = "Fix OK"
                                
                                # Satélites
                                self.last_data["satelites"] = int(msg.num_sats)
                                
                                if msg.altitude:
                                    self.last_data["altitud_ft"] = float(msg.altitude) 

                except pynmea2.ParseError:
                    continue 

        except Exception as e:
            return {
        'latitud': None, 'longitud': None, 'altitud_m': None, 
        'rumbo_deg': None, 'velocidad_kmh': None, 'satelites': None, 
        'error_gps': str(e)}

        # Devolvemos el diccionario con los últimos valores conocidos combinados
        return self.last_data