"""Tests unitarios para CSVLogger."""

import csv
import os
import pytest
from boya.logging.CSVlogger import CSVLogger


@pytest.fixture
def csv_path(tmp_path):
    """Retorna un path temporal para el archivo CSV de test."""
    return str(tmp_path / "test_datos.csv")


@pytest.fixture
def logger(csv_path):
    """Crea un CSVLogger apuntando a un archivo temporal."""
    return CSVLogger(filename=csv_path)


class TestCSVLoggerInit:
    """Tests de inicialización del logger CSV."""

    def test_init_con_nombre_por_defecto(self):
        """El nombre por defecto del archivo es datos_boya.csv."""
        logger = CSVLogger()
        assert logger.filename == "datos_boya.csv"

    def test_init_con_nombre_personalizado(self, csv_path):
        """Se puede especificar un nombre de archivo personalizado."""
        logger = CSVLogger(filename=csv_path)
        assert logger.filename == csv_path

    def test_header_fijo_definido(self):
        """El header fijo contiene todas las columnas esperadas."""
        logger = CSVLogger()
        columnas_esperadas = [
            "timestamp_local", "temperatura_C", "ph_value",
            "oxigeno_disuelto_mgL", "latitud", "longitud",
            "altitud_m", "rumbo_deg", "velocidad_kmh", "satelites",
            "error_temp", "error_ph", "error_od", "error_gps",
        ]
        assert logger.header == columnas_esperadas


class TestCSVLoggerLog:
    """Tests de escritura del logger CSV."""

    def test_crear_archivo_nuevo_con_header(self, logger, csv_path):
        """La primera escritura crea el archivo con encabezados."""
        datos = {"timestamp_local": "2026-03-03 15:00:00", "temperatura_C": 25.5}
        logger.log(datos)

        with open(csv_path, "r") as f:
            reader = csv.reader(f)
            filas = list(reader)

        assert len(filas) == 2  # header + 1 fila de datos
        assert filas[0] == CSVLogger.FIXED_HEADER

    def test_append_sin_duplicar_header(self, logger, csv_path):
        """Escrituras sucesivas no duplican el encabezado."""
        datos1 = {"timestamp_local": "2026-03-03 15:00:00", "temperatura_C": 25.0}
        datos2 = {"timestamp_local": "2026-03-03 15:05:00", "temperatura_C": 26.0}

        logger.log(datos1)
        logger.log(datos2)

        with open(csv_path, "r") as f:
            reader = csv.reader(f)
            filas = list(reader)

        assert len(filas) == 3  # header + 2 filas de datos

    def test_datos_parciales_completa_con_none(self, logger, csv_path):
        """Campos no proporcionados se escriben como vacíos (None)."""
        datos = {"timestamp_local": "2026-03-03 15:00:00"}
        logger.log(datos)

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            fila = next(reader)

        assert fila["timestamp_local"] == "2026-03-03 15:00:00"
        assert fila["temperatura_C"] == ""  # None se serializa como vacío en CSV

    def test_datos_completos(self, logger, csv_path):
        """Todos los campos se escriben correctamente."""
        datos = {
            "timestamp_local": "2026-03-03 15:00:00",
            "temperatura_C": 22.3,
            "ph_value": 7.1,
            "oxigeno_disuelto_mgL": 8.5,
            "latitud": -34.6037,
            "longitud": -58.3816,
            "altitud_m": 25.0,
            "rumbo_deg": 90.0,
            "velocidad_kmh": 5.5,
            "satelites": 8,
        }
        logger.log(datos)

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            fila = next(reader)

        assert fila["temperatura_C"] == "22.3"
        assert fila["ph_value"] == "7.1"
        assert fila["latitud"] == "-34.6037"
        assert fila["satelites"] == "8"

    def test_datos_con_errores_de_sensores(self, logger, csv_path):
        """Los errores de sensores se registran correctamente."""
        datos = {
            "timestamp_local": "2026-03-03 15:00:00",
            "error_temp": "Sensor no disponible",
            "error_gps": "Sin fix GPS",
        }
        logger.log(datos)

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            fila = next(reader)

        assert fila["error_temp"] == "Sensor no disponible"
        assert fila["error_gps"] == "Sin fix GPS"

    def test_no_crashea_con_directorio_invalido(self):
        """Si el directorio no existe, no lanza excepción (captura interna)."""
        logger = CSVLogger(filename="/ruta/inexistente/datos.csv")
        datos = {"timestamp_local": "2026-03-03 15:00:00"}
        # No debería lanzar excepción (el error se imprime internamente)
        logger.log(datos)
