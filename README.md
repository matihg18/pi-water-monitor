# pi-water-monitor

Este proyecto consiste en el software para una boya de monitoreo ambiental basada en **Raspberry Pi**. El sistema recolecta datos de calidad del agua (pH, Oxígeno Disuelto, Temperatura) y coordenadas GPS, almacenándolos en un archivo CSV para su posterior análisis. El proyecto es llevado adelante por alumnos y becarios de la Universidad Tecnológica Nacional Facultad Regional Concepción del Uruguay que participan del grupo de investigación GERU ("Grupo de Estudio del Río Uruguay"), tanto de la carrera de Ingeniería Civil como de Ingeniería en Sitemas de Información.

## Características principaless
- **Arquitectura Modular**: Sensores organizados mediante una interfaz común (`ISensor`).
- **Logging**: Sistema de guardado en CSV, pero ampliable bajo el uso de una interfaz común (`ILogger`).

## Hardware Compatible
- **Raspberry Pi** (Creado usando Raspberry Pi 3 Model B).
- **Sensores Atlas Scientific EZO** (pH y DO).
- **Sensor de Temperatura DS18B20**.
- **Módulo GPS** (NMEA).

## Configuración

El sistema requiere una **Raspberry Pi** con las siguientes interfaces habilitadas mediante `sudo raspi-config`:

* **I2C:** Necesario para los sensores Atlas Scientific (pH y OD).
* **1-Wire:** Para el sensor de temperatura DS18B20.
* **Serial (UART):** Para el módulo GPS.

Además necesitará crearse el entorno virtual de Python para instalar las dependencias del proyecto. Por eso una vez clonado el repositorio ejecute:
```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```


## Estructura del Proyecto
```text
proyecto-boya/
├── main.py                 # Punto de entrada y bucle principal
└── boya/
    ├── boya.py             # Clase entidad que coordina las mediciones
    ├── lib/
    │   └── AtlasI2C.py     # Módulo de soporte para sensores Atlas Scientific
    ├── logging/            
    │   ├── ilogger.py      # Interfaz base para el sistema de logging
    │   └── CSVlogger.py    # Implementación de guardado en formato CSV
    └── sensores/
        ├── isensor.py      # Interfaz base para todos los sensores
        ├── sensor_gps.py   # Gestión de coordenadas y datos NMEA
        ├── sensor_od.py    # Medición de Oxígeno Disuelto
        ├── sensor_ph.py    # Medición de potencial de Hidrógeno
        └── sensor_temp.py  # Medición de temperatur
```
