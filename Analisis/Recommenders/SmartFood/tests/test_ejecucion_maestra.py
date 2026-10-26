import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.execute_notebooks import NOTEBOOKS, ejecutar_secuencia


class EjecucionMaestraTest(unittest.TestCase):
    def test_detiene_secuencia_en_el_primer_error(self):
        with TemporaryDirectory(dir=Path(__file__).resolve().parent) as carpeta:
            with patch("scripts.execute_notebooks.ejecutar_notebook", side_effect=[None, RuntimeError("fallo controlado")]) as ejecutar:
                with contextlib.redirect_stdout(io.StringIO()):
                    estado = ejecutar_secuencia(Path(carpeta), timeout=10)
            resumen = json.loads((Path(carpeta) / "reports/ejecucion/resumen.json").read_text(encoding="utf-8"))
            self.assertEqual(estado, 1)
            self.assertEqual(ejecutar.call_count, 2)
            self.assertEqual(resumen["estado"], "error")
            self.assertEqual(resumen["notebooks"][0]["estado"], "completado")
            self.assertEqual(resumen["notebooks"][1]["estado"], "error")
            self.assertEqual([r["notebook"] for r in resumen["notebooks"]], NOTEBOOKS[:2])

    def test_completa_las_cinco_etapas_en_orden(self):
        with TemporaryDirectory(dir=Path(__file__).resolve().parent) as carpeta:
            with patch("scripts.execute_notebooks.ejecutar_notebook") as ejecutar:
                with contextlib.redirect_stdout(io.StringIO()):
                    estado = ejecutar_secuencia(Path(carpeta), timeout=10)
            self.assertEqual(estado, 0)
            self.assertEqual([c.args[0].name for c in ejecutar.call_args_list], NOTEBOOKS)
            resumen = json.loads((Path(carpeta) / "reports/ejecucion/resumen.json").read_text(encoding="utf-8"))
            self.assertEqual(resumen["estado"], "completado")
            self.assertTrue(all(r["estado"] == "completado" for r in resumen["notebooks"]))


if __name__ == "__main__":
    unittest.main()
