"""Tests unitarios para SensorOD con hardware mockeado."""

import pytest
from unittest.mock import patch, MagicMock
from boya.sensores.sensor_od import SensorOD


class TestSensorODInit:
    """Tests de inicialización del sensor de oxígeno disuelto."""

    @patch("boya.sensores.sensor_od.AtlasI2C")
    def test_init_exitoso(self, mock_atlas_class):
        """El sensor DO se inicializa correctamente."""
        sensor = SensorOD()
        mock_atlas_class.assert_called_once_with(address=97, moduletype="DO")
        assert sensor.do_sensor is not None

    @patch("boya.sensores.sensor_od.AtlasI2C")
    def test_init_con_error(self, mock_atlas_class):
        """Si falla la inicialización I2C, do_sensor queda en None."""
        mock_atlas_class.side_effect = IOError("I2C bus not available")
        sensor = SensorOD()
        assert sensor.do_sensor is None


class TestSensorODRead:
    """Tests de lectura del sensor de oxígeno disuelto."""

    @patch("boya.sensores.sensor_od.time")
    @patch("boya.sensores.sensor_od.AtlasI2C")
    def test_lectura_exitosa(self, mock_atlas_class, mock_time):
        """Lectura normal retorna el valor de oxígeno disuelto."""
        mock_instance = MagicMock()
        mock_instance.short_timeout = 0.3
        mock_instance.query.return_value = "Success DO 97: 8.5"
        mock_atlas_class.return_value = mock_instance

        sensor = SensorOD()
        resultado = sensor.read()

        assert resultado == {"oxigeno_disuelto_mgL": 8.5}
        mock_instance.query.assert_called_once_with("R")

    @patch("boya.sensores.sensor_od.time")
    @patch("boya.sensores.sensor_od.AtlasI2C")
    def test_compensacion_temperatura_por_defecto(self, mock_atlas_class, mock_time):
        """Sin temperatura explícita, usa 20.0°C como valor por defecto."""
        mock_instance = MagicMock()
        mock_instance.short_timeout = 0.3
        mock_instance.query.return_value = "Success DO 97: 9.0"
        mock_atlas_class.return_value = mock_instance

        sensor = SensorOD()
        sensor.read()

        # Verifica que se envía T,20.0 (temperatura por defecto)
        mock_instance.write.assert_called_once_with("T,20.0")

    @patch("boya.sensores.sensor_od.time")
    @patch("boya.sensores.sensor_od.AtlasI2C")
    def test_compensacion_temperatura_personalizada(self, mock_atlas_class, mock_time):
        """Se puede pasar una temperatura para compensación."""
        mock_instance = MagicMock()
        mock_instance.short_timeout = 0.3
        mock_instance.query.return_value = "Success DO 97: 7.8"
        mock_atlas_class.return_value = mock_instance

        sensor = SensorOD()
        sensor.read(temp_c_value=15.3)

        mock_instance.write.assert_called_once_with("T,15.3")

    def test_lectura_sin_sensor_conectado(self):
        """Si el sensor no está conectado, retorna error descriptivo."""
        sensor = SensorOD.__new__(SensorOD)
        sensor.do_sensor = None

        resultado = sensor.read()

        assert "error_do" in resultado
        assert "no conectado" in resultado["error_do"]

    @patch("boya.sensores.sensor_od.time")
    @patch("boya.sensores.sensor_od.AtlasI2C")
    def test_respuesta_de_error_del_sensor(self, mock_atlas_class, mock_time):
        """Si el sensor retorna un error (sin 'Success'), se captura."""
        mock_instance = MagicMock()
        mock_instance.short_timeout = 0.3
        mock_instance.query.return_value = "Error DO 97: 254"
        mock_atlas_class.return_value = mock_instance

        sensor = SensorOD()
        resultado = sensor.read()

        assert "error_do_status" in resultado
        assert "Error DO 97: 254" in resultado["error_do_status"]

    @patch("boya.sensores.sensor_od.time")
    @patch("boya.sensores.sensor_od.AtlasI2C")
    def test_excepcion_durante_lectura(self, mock_atlas_class, mock_time):
        """Una excepción durante la lectura retorna el error."""
        mock_instance = MagicMock()
        mock_instance.short_timeout = 0.3
        mock_instance.query.side_effect = IOError("I2C read failed")
        mock_atlas_class.return_value = mock_instance

        sensor = SensorOD()
        resultado = sensor.read()

        assert "error_od" in resultado
        assert "I2C read failed" in resultado["error_od"]

    @patch("boya.sensores.sensor_od.time")
    @patch("boya.sensores.sensor_od.AtlasI2C")
    def test_orden_write_antes_de_query(self, mock_atlas_class, mock_time):
        """Se envía compensación de temperatura ANTES de la lectura."""
        mock_instance = MagicMock()
        mock_instance.short_timeout = 0.3
        mock_instance.query.return_value = "Success DO 97: 8.0"
        mock_atlas_class.return_value = mock_instance

        sensor = SensorOD()
        sensor.read()

        # Verificar orden: primero write, luego sleep, luego query
        calls = mock_instance.method_calls
        write_idx = next(i for i, c in enumerate(calls) if c[0] == "write")
        query_idx = next(i for i, c in enumerate(calls) if c[0] == "query")
        assert write_idx < query_idx, "write() debe ejecutarse antes que query()"
