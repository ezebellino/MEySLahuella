import tempfile
import unittest
from pathlib import Path

from src.app.antena_services import editar_potencia, leer_configuracion


class AntenaServicesTests(unittest.TestCase):
    def test_leer_configuracion_devuelve_host_y_potencia(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ini_path = Path(tmp_dir) / "TciNumero.ini"
            ini_path.write_text("[ANTENA_UIP]\nREMOTE_HOST=10.0.0.5\nPOTENCIA=12\n", encoding="utf-8")

            remote_host, potencia = leer_configuracion(str(ini_path))

            self.assertEqual(remote_host, "10.0.0.5")
            self.assertEqual(potencia, "12")

    def test_editar_potencia_actualiza_el_archivo(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ini_path = Path(tmp_dir) / "TciNumero.ini"
            ini_path.write_text("[ANTENA_UIP]\nREMOTE_HOST=10.0.0.5\nPOTENCIA=12\n", encoding="utf-8")

            editar_potencia(str(ini_path), "20")
            _, potencia = leer_configuracion(str(ini_path))

            self.assertEqual(potencia, "20")

    def test_editar_potencia_valida_rango(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ini_path = Path(tmp_dir) / "TciNumero.ini"
            ini_path.write_text("[ANTENA_UIP]\nREMOTE_HOST=10.0.0.5\nPOTENCIA=12\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                editar_potencia(str(ini_path), "31")


if __name__ == "__main__":
    unittest.main()
