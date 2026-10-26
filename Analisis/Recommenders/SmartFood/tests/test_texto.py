import unittest

import numpy as np

from smartfood.texto import texto_ingredientes


class TextoIngredientesTest(unittest.TestCase):
    def test_formatos_de_parquet_y_texto_preparado(self):
        for valor in (["chicken", " garlic "], ("chicken", "garlic"), np.array(["chicken", "garlic"])):
            self.assertEqual(texto_ingredientes(valor), "chicken garlic")
        self.assertEqual(texto_ingredientes("chicken garlic"), "chicken garlic")
        self.assertEqual(texto_ingredientes(["chicken", None, np.nan, ""]), "chicken")

    def test_ausentes_y_vacios(self):
        for valor in (None, np.nan, [], np.array([]), " ", [None, ""]):
            self.assertIsNone(texto_ingredientes(valor))

    def test_no_convierte_tipos_invalidos_silenciosamente(self):
        with self.assertRaises(TypeError):
            texto_ingredientes(["chicken", 123])
        with self.assertRaises(ValueError):
            texto_ingredientes(np.array([["chicken"]]))


if __name__ == "__main__":
    unittest.main()
