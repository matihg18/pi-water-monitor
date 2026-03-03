"""Tests unitarios para SensorTemp con hardware mockeado."""

import sys
import pytest
from unittest.mock import patch, MagicMock
from boya.sensores.sensor_temp import SensorTemp
from w1thermsensor import NoSensorFoundError


class TestSensorTempInit:
    """Tests de inicialización del sensor de temperatura."""

    @patch("boya.sensores.sensor_temp.W1ThermSensor")
    def test_init_exitoso(self, mock_w1_class):
        """El sensor se inicializa correctamente cuando el hardware está presente."""
        sensor = SensorTemp()
        mock_w1_class.assert_called_once()
        assert sensor.sensor is not None

    @patch("boya.sensores.sensor_temp.W1ThermSensor")
    def test_init_sensor_no_encontrado(self, mock_w1_class):
        """Cuando no se encuentra el DS18B20, sensor queda en None."""
        mock_w1_class.side_effect = NoSensorFoundError("DS18B20")
        sensor = SensorTemp()
        assert sensor.sensor is None

    @patch("boya.sensores.sensor_temp.W1ThermSensor")
    def test_init_error_general(self, mock_w1_class):
        """Un error inesperado al inicializar deja sensor en None."""
        mock_w1_class.side_effect = RuntimeError("Bus I/O error")
        sensor = SensorTemp()
        assert sensor.sensor is None


class TestSensorTempRead:
    """Tests de lectura del sensor de temperatura."""

    @patch("boya.sensores.sensor_temp.W1ThermSensor")
    def test_lectura_exitosa(self, mock_w1_class):
        """Lectura normal retorna la temperatura en un diccionario."""
        mock_instance = MagicMock()
        mock_instance.get_temperature.return_value = 25.5
        mock_w1_class.return_value = mock_instance

        sensor = SensorTemp()
        resultado = sensor.read()

        assert resultado == {"temperatura_C": 25.5}
        mock_instance.get_temperature.assert_called_once()

    @patch("boya.sensores.sensor_temp.W1ThermSensor")
    def test_lectura_con_temperatura_negativa(self, mock_w1_class):
        """El sensor puede leer temperaturas bajo cero."""
        mock_instance = MagicMock()
        mock_instance.get_temperature.return_value = -3.2
        mock_w1_class.return_value = mock_instance

        sensor = SensorTemp()
        resultado = sensor.read()

        assert resultado == {"temperatura_C": -3.2}

    def test_lectura_sin_sensor_disponible(self):
        """Si el sensor no está disponible, retorna un error descriptivo."""
        sensor = SensorTemp.__new__(SensorTemp)
        sensor.sensor = None

        resultado = sensor.read()

        assert "error_temp" in resultado
        assert "no disponible" in resultado["error_temp"]

    @patch("boya.sensores.sensor_temp.W1ThermSensor")
    def test_lectura_con_excepcion(self, mock_w1_class):
        """Si la lectura falla, retorna el error como string."""
        mock_instance = MagicMock()
        mock_instance.get_temperature.side_effect = OSError("CRC check failed")
        mock_w1_class.return_value = mock_instance

        sensor = SensorTemp()
        resultado = sensor.read()

        assert "error_temp_reading" in resultado
        assert "CRC check failed" in resultado["error_temp_reading"]
