import random
import time
from boya.sensores.isensor import ISensor

class MockSensorTemp(ISensor):
    """Simula un sensor de temperatura DS18B20 con fluctuaciones realistas."""
    def __init__(self):
        self.current_temp = 20.0
        print("MOCK: Sensor de Temperatura DS18B20 inicializado (Simulación)")

    def read(self) -> dict:
        # Pequeña variación de +/- 0.1 grados
        self.current_temp += random.uniform(-0.1, 0.1)
        return {"temperatura_C": round(self.current_temp, 2)}

class MockSensorPH(ISensor):
    """Simula un sensor de pH Atlas EZO."""
    def __init__(self):
        self.current_ph = 7.0
        print("MOCK: Sensor pH inicializado (Simulación)")

    def read(self) -> dict:
        self.current_ph += random.uniform(-0.02, 0.02)
        # Mantener en rango típico de agua de río
        self.current_ph = max(6.5, min(8.5, self.current_ph))
        return {"ph_value": round(self.current_ph, 2)}

class MockSensorOD(ISensor):
    """Simula un sensor de Oxígeno Disuelto Atlas EZO."""
    def __init__(self):
        self.current_do = 8.0
        print("MOCK: Sensor DO inicializado (Simulación)")

    def read(self, temp_c_value=None) -> dict:
        # El DO suele bajar si la temperatura sube
        variation = random.uniform(-0.05, 0.05)
        if temp_c_value and temp_c_value > 25:
            variation -= 0.1
        
        self.current_do += variation
        self.current_do = max(4.0, min(12.0, self.current_do))
        return {"oxigeno_disuelto_mgL": round(self.current_do, 2)}

class MockSensorGPS(ISensor):
    """Simula un GPS moviéndose levemente (deriva en el río)."""
    def __init__(self):
        # Coordenadas aproximadas de Concepción del Uruguay (Río Uruguay)
        self.lat = -32.4845
        self.lon = -58.2100
        print("MOCK: Sensor GPS inicializado (Simulación)")

    def read(self) -> dict:
        # Simular deriva lenta
        self.lat += random.uniform(-0.0001, 0.0001)
        self.lon += random.uniform(-0.0001, 0.0001)
        
        return {
            "latitud": round(self.lat, 6),
            "longitud": round(self.lon, 6),
            "altitud_m": 12.5,
            "rumbo_deg": random.uniform(0, 360),
            "velocidad_kmh": random.uniform(0.5, 2.5),
            "satelites": 10,
            "gps_status": "Fix OK (Sim)"
        }
    
    def close(self):
        print("MOCK: GPS cerrado.")
