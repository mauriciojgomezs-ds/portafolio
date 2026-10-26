"""Reglas de interpretación: cambios de resultado y casos no definidos."""

import unittest

import pandas as pd

from smartfood.anotaciones import (
    comentario_clasificacion,
    comentario_correlacion,
    comentario_nmf,
    comentario_recomendaciones,
)


class AnotacionesTest(unittest.TestCase):
    def test_correlacion_direccion_y_datos_invalidos(self):
        df = pd.DataFrame({"x": [1, 2, 3, None, float("inf")], "y": [3, 2, 1, 9, 8]})
        texto = comentario_correlacion(df, "x", "y")
        self.assertIn("negativa, muy fuerte", texto)
        self.assertIn("3 pares válidos", texto)
        self.assertIn("2 filas excluidas", texto)
        self.assertIn("positiva, muy fuerte", comentario_correlacion(pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]}), "x", "y", "spearman"))

    def test_correlacion_no_definida(self):
        self.assertIn("menos de tres", comentario_correlacion(pd.DataFrame({"x": [1, 2], "y": [1, 2]}), "x", "y"))
        self.assertIn("constante", comentario_correlacion(pd.DataFrame({"x": [1, 1, 1], "y": [1, 2, 3]}), "x", "y"))
        with self.assertRaises(ValueError):
            comentario_correlacion(pd.DataFrame(), "x", "y", cortes=(0.3, 0.1, 0.5, 0.7))

    def test_intensidad_configurable(self):
        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [1, 3, 2, 4]})
        self.assertIn("muy fuerte", comentario_correlacion(df, "x", "y"))
        self.assertIn("fuerte", comentario_correlacion(df, "x", "y", cortes=(0.1, 0.3, 0.5, 0.9)))
        self.assertNotIn("muy fuerte", comentario_correlacion(df, "x", "y", cortes=(0.1, 0.3, 0.5, 0.9)))

    def test_recomendaciones(self):
        self.assertIn("No se obtuvieron", comentario_recomendaciones([], 5))
        self.assertIn("incompleta", comentario_recomendaciones([1, 2], 5))
        self.assertIn("alcanza", comentario_recomendaciones([1, 2], 2))

    def test_nmf_minimo_empate_y_ausencia(self):
        grid = pd.DataFrame({"rmse": [4.2, 4.2, 4.5]}, index=[10, 20, 70])
        self.assertIn("10, 20 componentes", comentario_nmf(grid, 10))
        self.assertIn("alcanza", comentario_nmf(grid, 20))
        self.assertIn("no minimiza", comentario_nmf(grid, 70))
        self.assertIn("no tiene", comentario_nmf(grid, 99))
        self.assertIn("No hay RMSE", comentario_nmf(pd.DataFrame({"rmse": [float("nan")]}), 1))

    def test_clasificacion_baseline_de_train_y_clase_ausente(self):
        # Train majority is 0 although the majority in this test is 1.
        texto = comentario_clasificacion([0, 0, 1], [0, 1, 1], [1, 1, 1])
        self.assertIn("supera", texto)
        self.assertIn("clase **1**", texto)
        self.assertIn("**33,33 %**", texto)
        self.assertIn("iguala", comentario_clasificacion([1, 1, 0], [0, 1], [1, 1]))
        self.assertIn("queda por debajo", comentario_clasificacion([1, 1, 0], [1, 1, 0], [0, 0, 0]))
        self.assertIn("no disponible", comentario_clasificacion([0, 1], [1, 1], [1, 1]))
        with self.assertRaises(ValueError):
            comentario_clasificacion([0, 1], [0], [0, 1])


if __name__ == "__main__":
    unittest.main()
