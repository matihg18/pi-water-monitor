"""Tests de integración para la clase Boya con sensores mockeados."""

import pytest
from unittest.mock import MagicMock, patch, call


class TestBoyaInit:
    """Tests de inicialización de la clase Boya."""

    def test_inyeccion_de_dependencias(self):
        """Boya almacena las dependencias inyectadas correctamente."""
        from boya.boya import Boya

        mock_temp = MagicMock()
        mock_do = MagicMock()
        mock_ph = MagicMock()
        mock_gps = MagicMock()
        mock_logger = MagicMock()

        boya = Boya(
            temp_sensor=mock_temp,
            do_sensor=mock_do,
            ph_sensor=mock_ph,
            gps_sensor=mock_gps,
            logger=mock_logger,
        )

        assert boya.temp_sensor is mock_temp
        assert boya.do_sensor is mock_do
        assert boya.ph_sensor is mock_ph
        assert boya.gps_sensor is mock_gps
        assert boya.logger is mock_logger


class TestBoyaRun:
    """Tests del ciclo principal de medición.

    Para testear el while True loop, usamos side_effect en time.sleep
    para lanzar una excepción que rompa el loop después de la primera iteración.
    """

    def _crear_boya_con_mocks(self):
        """Helper: crea una Boya con todos los sensores mockeados."""
        from boya.boya import Boya

        mock_temp = MagicMock()
        mock_temp.read.return_value = {"temperatura_C": 22.5}

        mock_do = MagicMock()
        mock_do.read.return_value = {"oxigeno_disuelto_mgL": 8.2}

        mock_ph = MagicMock()
        mock_ph.read.return_value = {"ph_value": 7.0}

        mock_gps = MagicMock()
        mock_gps.read.return_value = {
            "latitud": -34.6037,
            "longitud": -58.3816,
            "altitud_m": 25.0,
            "rumbo_deg": 90.0,
            "velocidad_kmh": 5.5,
            "satelites": 8,
            "gps_status": "Fix OK",
        }

        mock_logger = MagicMock()

        boya = Boya(
            temp_sensor=mock_temp,
            do_sensor=mock_do,
            ph_sensor=mock_ph,
            gps_sensor=mock_gps,
            logger=mock_logger,
        )

        return boya, mock_temp, mock_do, mock_ph, mock_gps, mock_logger

    @patch("boya.boya.time")
    def test_ciclo_completo_exitoso(self, mock_time):
        """Todos los sensores se leen y los datos se loguean."""
        # Romper el loop después de la primera iteración
        mock_time.sleep.side_effect = StopIteration
        mock_time.strftime.return_value = "2026-03-03 15:00:00"

        boya, mock_temp, mock_do, mock_ph, mock_gps, mock_logger = (
            self._crear_boya_con_mocks()
        )

        with pytest.raises(StopIteration):
            boya.run(interval_seg=5)

        # Todos los sensores fueron leídos
        mock_temp.read.assert_called_once()
        mock_do.read.assert_called_once()
        mock_ph.read.assert_called_once()
        mock_gps.read.assert_called_once()

        # El logger recibió los datos combinados
        mock_logger.log.assert_called_once()
        datos_logueados = mock_logger.log.call_args[0][0]

        assert datos_logueados["timestamp_local"] == "2026-03-03 15:00:00"
        assert datos_logueados["temperatura_C"] == 22.5
        assert datos_logueados["oxigeno_disuelto_mgL"] == 8.2
        assert datos_logueados["ph_value"] == 7.0
        assert datos_logueados["latitud"] == -34.6037

    @patch("boya.boya.time")
    def test_todos_los_sensores_reciben_read(self, mock_time):
        """Verifica que cada sensor recibe exactamente una llamada a read()."""
        mock_time.sleep.side_effect = StopIteration
        mock_time.strftime.return_value = "2026-03-03 15:00:00"

        boya, mock_temp, mock_do, mock_ph, mock_gps, _ = (
            self._crear_boya_con_mocks()
        )

        with pytest.raises(StopIteration):
            boya.run()

        for sensor_mock in [mock_temp, mock_ph, mock_gps]:
            sensor_mock.read.assert_called_once()
        # OD recibe temperatura como parámetro
        mock_do.read.assert_called_once_with(temp_c_value=22.5)

    @patch("boya.boya.time")
    def test_logger_recibe_datos_consolidados(self, mock_time):
        """El logger recibe un único diccionario con datos de todos los sensores."""
        mock_time.sleep.side_effect = StopIteration
        mock_time.strftime.return_value = "2026-03-03 15:00:00"

        boya, _, _, _, _, mock_logger = self._crear_boya_con_mocks()

        with pytest.raises(StopIteration):
            boya.run()

        datos = mock_logger.log.call_args[0][0]

        # Claves de cada sensor presentes
        assert "timestamp_local" in datos
        assert "temperatura_C" in datos
        assert "oxigeno_disuelto_mgL" in datos
        assert "ph_value" in datos
        assert "latitud" in datos
        assert "longitud" in datos

    @patch("boya.boya.time")
    def test_error_en_sensor_no_detiene_el_ciclo(self, mock_time):
        """Si un sensor lanza una excepción, el error se captura y el loop continúa."""
        # Permitir 2 iteraciones: la primera con error, la segunda OK
        call_count = 0

        def sleep_side_effect(secs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                raise StopIteration

        mock_time.sleep.side_effect = sleep_side_effect
        mock_time.strftime.return_value = "2026-03-03 15:00:00"

        boya, mock_temp, mock_do, mock_ph, mock_gps, mock_logger = (
            self._crear_boya_con_mocks()
        )

        # El sensor de temperatura falla en la primera iteración
        mock_temp.read.side_effect = [
            RuntimeError("Sensor disconnected"),
            {"temperatura_C": 20.0},
        ]

        with pytest.raises(StopIteration):
            boya.run(interval_seg=1)

        # El loop continuó a la segunda iteración (time.sleep se llamó 2 veces)
        assert mock_time.sleep.call_count == 2

    @patch("boya.boya.time")
    def test_intervalo_de_medicion_personalizado(self, mock_time):
        """El intervalo de medición se pasa correctamente a time.sleep."""
        mock_time.sleep.side_effect = StopIteration
        mock_time.strftime.return_value = "2026-03-03 15:00:00"

        boya, _, _, _, _, _ = self._crear_boya_con_mocks()

        with pytest.raises(StopIteration):
            boya.run(interval_seg=10)

        mock_time.sleep.assert_called_with(10)

    @patch("boya.boya.time")
    def test_timestamp_se_genera_en_cada_iteracion(self, mock_time):
        """Cada iteración genera un nuevo timestamp."""
        call_count = 0

        def sleep_side_effect(secs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                raise StopIteration

        mock_time.sleep.side_effect = sleep_side_effect
        mock_time.strftime.side_effect = [
            "2026-03-03 15:00:00",
            "2026-03-03 15:00:05",
        ]

        boya, _, _, _, _, mock_logger = self._crear_boya_con_mocks()

        with pytest.raises(StopIteration):
            boya.run(interval_seg=5)

        # strftime se llamó 2 veces (una por iteración)
        assert mock_time.strftime.call_count == 2

    @patch("boya.boya.time")
    def test_sensor_retorna_error_dict_se_loguea(self, mock_time):
        """Los sensores que retornan errores como dict se incluyen en el log."""
        mock_time.sleep.side_effect = StopIteration
        mock_time.strftime.return_value = "2026-03-03 15:00:00"

        boya, mock_temp, _, _, _, mock_logger = self._crear_boya_con_mocks()

        # El sensor de temp retorna un error (sin crash)
        mock_temp.read.return_value = {"error_temp": "Sensor no disponible"}

        with pytest.raises(StopIteration):
            boya.run()

        datos = mock_logger.log.call_args[0][0]
        assert datos["error_temp"] == "Sensor no disponible"

    @patch("boya.boya.time")
    def test_od_recibe_temperatura_real(self, mock_time):
        """El sensor OD recibe la temperatura real para compensación."""
        mock_time.sleep.side_effect = StopIteration
        mock_time.strftime.return_value = "2026-03-03 15:00:00"

        boya, mock_temp, mock_do, _, _, _ = self._crear_boya_con_mocks()

        with pytest.raises(StopIteration):
            boya.run()

        # El sensor OD recibió la temperatura del sensor de temp
        mock_do.read.assert_called_once_with(temp_c_value=22.5)

    @patch("boya.boya.time")
    def test_od_recibe_none_si_temp_falla(self, mock_time):
        """Si el sensor de temp retorna error, OD recibe None como temperatura."""
        mock_time.sleep.side_effect = StopIteration
        mock_time.strftime.return_value = "2026-03-03 15:00:00"

        boya, mock_temp, mock_do, _, _, _ = self._crear_boya_con_mocks()
        mock_temp.read.return_value = {"error_temp": "No disponible"}

        with pytest.raises(StopIteration):
            boya.run()

        # Sin temperatura disponible, se pasa None
        mock_do.read.assert_called_once_with(temp_c_value=None)


class TestBoyaClose:
    """Tests del cierre de recursos de la Boya."""

    def test_close_llama_close_de_gps(self):
        """close() invoca close() en el sensor GPS."""
        from boya.boya import Boya

        mock_gps = MagicMock()
        boya = Boya(
            temp_sensor=MagicMock(),
            do_sensor=MagicMock(),
            ph_sensor=MagicMock(),
            gps_sensor=mock_gps,
            logger=MagicMock(),
        )

        boya.close()

        mock_gps.close.assert_called_once()
