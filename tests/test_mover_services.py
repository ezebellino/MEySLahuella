import tempfile
import unittest
from pathlib import Path

from src.app.mover_services import find_and_move_files


class MoverServicesTests(unittest.TestCase):
    def test_mueve_archivos_dat_a_carpeta_fechada(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            source = Path(tmp_dir) / "source"
            destination = Path(tmp_dir) / "dest"
            nested = source / "nested"
            nested.mkdir(parents=True)
            destination.mkdir()
            (nested / "uno.dat").write_text("contenido", encoding="utf-8")
            (source / "dos.dat").write_text("contenido", encoding="utf-8")

            final_folder = find_and_move_files(str(source), str(destination))

            self.assertIsNotNone(final_folder)
            final_path = Path(final_folder)
            self.assertTrue((final_path / "uno.dat").exists())
            self.assertTrue((final_path / "dos.dat").exists())

    def test_devuelve_none_si_no_hay_archivos_dat(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            source = Path(tmp_dir) / "source"
            destination = Path(tmp_dir) / "dest"
            source.mkdir()
            destination.mkdir()
            (source / "archivo.txt").write_text("contenido", encoding="utf-8")

            final_folder = find_and_move_files(str(source), str(destination))

            self.assertIsNone(final_folder)


if __name__ == "__main__":
    unittest.main()
