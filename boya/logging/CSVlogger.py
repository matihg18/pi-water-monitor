import csv
import os
from boya.logging.ilogger import ILogger 

class CSVLogger(ILogger): 

    FIXED_HEADER = [
        'timestamp_local',
        'temperatura_C', 
        'ph_value', 
        'oxigeno_disuelto_mgL', 
        'latitud', 
        'longitud', 
        'altitud_m',
        'rumbo_deg',
        'velocidad_kmh',
        'satelites',
        'error_temp',        
        'error_ph',          
        'error_od',           
        'error_gps'           
    ]

    def __init__(self, filename="datos_boya.csv"):
        self.filename = filename
        self.header = self.FIXED_HEADER

    def log(self, data: dict):

        try:
            full_data = {key: data.get(key) for key in self.header}

            with open(self.filename, mode='a', newline='') as file:
                is_file_empty = file.tell() == 0 

                writer = csv.DictWriter(file, fieldnames=self.header) 
                
                if is_file_empty: 
                    writer.writeheader()
                
                writer.writerow(full_data) 
                
        except Exception as e:
            print(f"ERROR AL ESCRIBIR EN CSV: {e}")