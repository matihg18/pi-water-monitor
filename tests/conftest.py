"""
conftest.py - Configuración global de pytest.

Mockea módulos de hardware que no están disponibles fuera de la Raspberry Pi
(w1thermsensor, AtlasI2C vía fcntl/io, serial) para que los tests puedan
importar el código de producción sin errores.
"""

import sys
from unittest.mock import MagicMock

# ===================================================================
# Mock de w1thermsensor (requiere kernel modules de Raspberry Pi)
# ===================================================================
mock_w1thermsensor = MagicMock()


class _MockNoSensorFoundError(Exception):
    """Exception mock para NoSensorFoundError."""
    pass


mock_w1thermsensor.NoSensorFoundError = _MockNoSensorFoundError
mock_w1thermsensor.W1ThermSensor = MagicMock

sys.modules["w1thermsensor"] = mock_w1thermsensor

# ===================================================================
# Mock de fcntl (solo disponible en Linux con I2C)
# ===================================================================
if "fcntl" not in sys.modules:
    sys.modules["fcntl"] = MagicMock()
