"""Tests unitarios para SensorPH con hardware mockeado."""

import pytest
from unittest.mock import patch, MagicMock
from boya.sensores.sensor_ph import SensorPH


class TestSensorPHInit:
    """Tests de inicialización del sensor de pH."""

    @patch("boya.sensores.sensor_ph.AtlasI2C")
    def test_init_exitoso(self, mock_atlas_class):
        """El sensor pH se inicializa correctamente en la dirección I2C 99."""
        sensor = SensorPH()
        mock_atlas_class.assert_called_once_with(address=99, moduletype="pH")
        assert sensor.ph_sensor is not None

    @patch("boya.sensores.sensor_ph.AtlasI2C")
    def test_init_con_error(self, mock_atlas_class):
        """Si falla la inicialización I2C, ph_sensor queda en None."""
        mock_atlas_class.side_effect = IOError("I2C bus not available")
        sensor = SensorPH()
        assert sensor.ph_sensor is None


class TestSensorPHRead:
    """Tests de lectura del sensor de pH."""

    @patch("boya.sensores.sensor_ph.AtlasI2C")
    def test_lectura_exitosa(self, mock_atlas_class):
        """Lectura normal retorna el valor de pH."""
        mock_instance = MagicMock()
        mock_instance.query.return_value = "Success pH 99: 7.2"
        mock_atlas_class.return_value = mock_instance

        sensor = SensorPH()
        resultado = sensor.read()

        assert resultado == {"ph_value": 7.2}
        mock_instance.query.assert_called_once_with("R")

    @patch("boya.sensores.sensor_ph.AtlasI2C")
    def test_lectura_ph_acido(self, mock_atlas_class):
        """El sensor puede leer valores ácidos (< 7)."""
        mock_instance = MagicMock()
        mock_instance.query.return_value = "Success pH 99: 3.5"
        mock_atlas_class.return_value = mock_instance

        sensor = SensorPH()
        resultado = sensor.read()

        assert resultado == {"ph_value": 3.5}

    @patch("boya.sensores.sensor_ph.AtlasI2C")
    def test_lectura_ph_basico(self, mock_atlas_class):
        """El sensor puede leer valores básicos (> 7)."""
        mock_instance = MagicMock()
        mock_instance.query.return_value = "Success pH 99: 12.1"
        mock_atlas_class.return_value = mock_instance

        sensor = SensorPH()
        resultado = sensor.read()

        assert resultado == {"ph_value": 12.1}

    def test_lectura_sin_sensor_conectado(self):
        """Si el sensor no está conectado, retorna error descriptivo."""
        sensor = SensorPH.__new__(SensorPH)
        sensor.ph_sensor = None

        resultado = sensor.read()

        assert "error_ph" in resultado
        assert "no conectado" in resultado["error_ph"]

    @patch("boya.sensores.sensor_ph.AtlasI2C")
    def test_respuesta_de_error_del_sensor(self, mock_atlas_class):
        """Si el sensor retorna un error (sin 'Success'), se captura."""
        mock_instance = MagicMock()
        mock_instance.query.return_value = "Error pH 99: 254"
        mock_atlas_class.return_value = mock_instance

        sensor = SensorPH()
        resultado = sensor.read()

        assert "error_ph_status" in resultado

    @patch("boya.sensores.sensor_ph.AtlasI2C")
    def test_excepcion_durante_lectura(self, mock_atlas_class):
        """Una excepción durante la lectura retorna el error."""
        mock_instance = MagicMock()
        mock_instance.query.side_effect = IOError("I2C read failed")
        mock_atlas_class.return_value = mock_instance

        sensor = SensorPH()
        resultado = sensor.read()

        assert "error_ph" in resultado
        assert "I2C read failed" in resultado["error_ph"]
