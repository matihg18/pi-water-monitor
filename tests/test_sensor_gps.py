"""Tests unitarios para SensorGPS con hardware mockeado."""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from boya.sensores.sensor_gps import SensorGPS


class TestSensorGPSInit:
    """Tests de inicialización del sensor GPS."""

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_init_exitoso(self, mock_serial_class):
        """El GPS se conecta correctamente al puerto serial."""
        sensor = SensorGPS(port="/dev/serial0", baudrate=9600)
        mock_serial_class.assert_called_once_with("/dev/serial0", 9600, timeout=1)
        assert sensor.serial_conn is not None

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_init_con_error(self, mock_serial_class):
        """Si falla la conexión serial, serial_conn queda en None."""
        mock_serial_class.side_effect = OSError("Port not found")
        sensor = SensorGPS()
        assert sensor.serial_conn is None

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_init_valores_por_defecto(self, mock_serial_class):
        """Los datos GPS iniciales tienen valores por defecto razonables."""
        sensor = SensorGPS()
        assert sensor.last_data["latitud"] is None
        assert sensor.last_data["longitud"] is None
        assert sensor.last_data["gps_status"] == "Iniciando"
        assert sensor.last_data["satelites"] == 0


class TestSensorGPSRead:
    """Tests de lectura del sensor GPS."""

    def test_lectura_sin_hardware(self):
        """Sin conexión serial retorna error de hardware."""
        sensor = SensorGPS.__new__(SensorGPS)
        sensor.serial_conn = None
        sensor.last_data = {}

        resultado = sensor.read()

        assert resultado == {"error_gps": "Error Hardware"}

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_lectura_sin_datos_en_buffer(self, mock_serial_class):
        """Si no hay datos en el buffer, retorna los datos por defecto."""
        mock_conn = MagicMock()
        mock_conn.in_waiting = 0
        mock_serial_class.return_value = mock_conn

        sensor = SensorGPS()
        resultado = sensor.read()

        assert resultado["gps_status"] == "Iniciando"
        assert resultado["latitud"] is None

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_lectura_sentencia_rmc_valida(self, mock_serial_class):
        """Una sentencia GPRMC válida actualiza posición, velocidad y rumbo."""
        mock_conn = MagicMock()
        # Sentencia GPRMC con fix válido (status='A')
        # Lat: 34°36.265'S, Lon: 58°22.475'W, Vel: 5.2 knots, Rumbo: 180.5°
        rmc_line = b"$GPRMC,123519,A,3436.265,S,05822.475,W,5.2,180.5,230394,003.1,W*68\r\n"

        # Simular in_waiting > 0 para la primera iteración, luego 0
        type(mock_conn).in_waiting = PropertyMock(side_effect=[1, 0])
        mock_conn.readline.return_value = rmc_line
        mock_serial_class.return_value = mock_conn

        sensor = SensorGPS()
        resultado = sensor.read()

        assert resultado["gps_status"] == "Fix OK"
        assert resultado["latitud"] is not None
        assert resultado["longitud"] is not None
        # Velocidad se convierte de knots a km/h (* 1.852)
        assert abs(resultado["velocidad_kmh"] - (5.2 * 1.852)) < 0.01
        assert resultado["rumbo_deg"] == 180.5

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_lectura_sentencia_gga_valida(self, mock_serial_class):
        """Una sentencia GPGGA válida actualiza altitud y satélites."""
        mock_conn = MagicMock()
        # Sentencia GPGGA con fix válido (quality=1), 8 satélites, altitud 54.7m
        gga_line = b"$GPGGA,123519,3436.265,S,05822.475,W,1,08,0.9,54.7,M,46.9,M,,*74\r\n"

        type(mock_conn).in_waiting = PropertyMock(side_effect=[1, 0])
        mock_conn.readline.return_value = gga_line
        mock_serial_class.return_value = mock_conn

        sensor = SensorGPS()
        resultado = sensor.read()

        assert resultado["gps_status"] == "Fix OK"
        assert resultado["satelites"] == 8
        assert resultado["altitud_m"] == 54.7

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_datos_nmea_corruptos_no_crashean(self, mock_serial_class):
        """Datos NMEA corruptos se ignoran sin provocar un crash."""
        mock_conn = MagicMock()
        corrupt_line = b"$GPXYZ,CORRUPTED,DATA*FF\r\n"

        type(mock_conn).in_waiting = PropertyMock(side_effect=[1, 0])
        mock_conn.readline.return_value = corrupt_line
        mock_serial_class.return_value = mock_conn

        sensor = SensorGPS()
        # No debería lanzar excepción
        resultado = sensor.read()

        # Retorna los valores por defecto (sin update)
        assert resultado["latitud"] is None

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_excepcion_general_durante_lectura(self, mock_serial_class):
        """Una excepción general retorna error con todos los campos en None."""
        mock_conn = MagicMock()
        type(mock_conn).in_waiting = PropertyMock(side_effect=OSError("Serial port error"))
        mock_serial_class.return_value = mock_conn

        sensor = SensorGPS()
        resultado = sensor.read()

        assert "error_gps" in resultado
        assert "Serial port error" in resultado["error_gps"]

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_multiples_sentencias_combinadas(self, mock_serial_class):
        """Se combinan datos de RMC y GGA en un solo diccionario."""
        mock_conn = MagicMock()
        rmc_line = b"$GPRMC,123519,A,3436.265,S,05822.475,W,5.2,180.5,230394,003.1,W*68\r\n"
        gga_line = b"$GPGGA,123519,3436.265,S,05822.475,W,1,08,0.9,54.7,M,46.9,M,,*74\r\n"

        # Simular 2 líneas disponibles y luego 0
        type(mock_conn).in_waiting = PropertyMock(side_effect=[1, 1, 0])
        mock_conn.readline.side_effect = [rmc_line, gga_line]
        mock_serial_class.return_value = mock_conn

        sensor = SensorGPS()
        resultado = sensor.read()

        # Datos de RMC
        assert resultado["gps_status"] == "Fix OK"
        assert abs(resultado["velocidad_kmh"] - (5.2 * 1.852)) < 0.01
        # Datos de GGA
        assert resultado["satelites"] == 8
        assert resultado["altitud_m"] == 54.7


class TestSensorGPSClose:
    """Tests de cierre del sensor GPS."""

    @patch("boya.sensores.sensor_gps.serial.Serial")
    def test_close_cierra_conexion_serial(self, mock_serial_class):
        """close() cierra la conexión serial correctamente."""
        mock_conn = MagicMock()
        mock_serial_class.return_value = mock_conn

        sensor = SensorGPS()
        sensor.close()

        mock_conn.close.assert_called_once()

    def test_close_sin_conexion_no_falla(self):
        """close() no falla si la conexión es None."""
        sensor = SensorGPS.__new__(SensorGPS)
        sensor.serial_conn = None
        # No debería lanzar excepción
        sensor.close()
