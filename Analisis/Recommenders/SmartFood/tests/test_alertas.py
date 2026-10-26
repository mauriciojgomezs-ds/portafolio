import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import warnings

from smartfood.entorno_notebook import configurar_notebook, obtener_alertas, mostrar_alertas


class AlertasTest(unittest.TestCase):
    def test_agrupa_repeticiones_y_conserva_detalles(self):
        with warnings.catch_warnings():
            configurar_notebook()
            for _ in range(3):
                warnings.warn("división inválida", RuntimeWarning)
            warnings.warn("otro aviso", UserWarning)
            registros = obtener_alertas()
            self.assertEqual(len(registros), 2)
            self.assertEqual(registros[0]["apariciones"], 3)
            self.assertTrue(registros[0]["origenes"])
            self.assertIn("numérica", registros[0]["descripcion"])
            copia = obtener_alertas()
            copia[0]["origenes"].clear()
            self.assertTrue(obtener_alertas()[0]["origenes"])
            configurar_notebook()
            self.assertEqual(obtener_alertas(), [])

    def test_html_seguro_y_exportacion(self):
        with warnings.catch_warnings():
            configurar_notebook()
            warnings.warn("<script>aviso</script>", UserWarning)
            with TemporaryDirectory(dir=Path(__file__).resolve().parent) as carpeta, patch("IPython.display.display") as display:
                destino = Path(carpeta) / "alertas.json"
                mostrar_alertas(destino)
                self.assertEqual(json.loads(destino.read_text(encoding="utf-8"))[0]["mensaje"], "<script>aviso</script>")
                html = display.call_args.args[0].data
                self.assertNotIn("<script>", html)
                self.assertIn("&lt;script&gt;", html)

    def test_no_intercepta_excepciones_y_sin_alertas(self):
        with warnings.catch_warnings():
            configurar_notebook()
            with self.assertRaises(ValueError):
                raise ValueError("error real")
            with patch("IPython.display.display") as display:
                mostrar_alertas()
                self.assertIn("no se registraron", display.call_args.args[0].data)


if __name__ == "__main__":
    unittest.main()
