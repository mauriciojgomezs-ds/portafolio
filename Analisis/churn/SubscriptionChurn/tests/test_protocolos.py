import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import zipfile

import pandas as pd

from subscription_churn.flujo import preparar, cargar, baseline, entrenar, evaluar, features


class FlujoTest(unittest.TestCase):
    def test_fuente_sin_id_y_codigo_categorico(self):
        with TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporal:
            raiz = Path(temporal)
            proyecto = raiz / "telecom"
            proyecto.mkdir()
            cfg = {"target": "Churn", "id": None, "exclude": [], "categorical_columns": ["Area code"], "source_zip": "../fuente.zip", "members": {"train": "train.csv", "test": "test.csv"}, "split": "provided"}
            (proyecto / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
            df = pd.DataFrame({"actividad": range(50), "Area code": [408, 415] * 25, "Churn": [False, True] * 25})
            with zipfile.ZipFile(raiz / "fuente.zip", "w") as z:
                z.writestr("train.csv", df.to_csv(index=False))
                z.writestr("test.csv", df.iloc[:8].to_csv(index=False))
            preparar(proyecto)
            info = json.loads((proyecto / "reports/preparacion/preparacion.json").read_text(encoding="utf-8"))
            self.assertIsNone(info["ids_compartidos_train_test"])
            self.assertEqual(info["filas_identicas_train_test"] + info["filas_identicas_valid_test"], 8)
            train = cargar(proyecto, "train")
            self.assertTrue(train.Churn.isin([0, 1]).all())
            self.assertTrue(features(train, cfg)["Area code"].map(lambda v: isinstance(v, str)).all())
            self.assertTrue(pd.api.types.is_numeric_dtype(train["Area code"]))

    def test_recorrido_y_target_ausente(self):
        with TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporal:
            raiz = Path(temporal)
            proyecto = raiz / "caso"
            proyecto.mkdir()
            cfg = {"target": "Churn", "id": "id", "exclude": ["id"], "source_zip": "../fuente.zip", "members": {"full": "datos.csv"}, "split": "stratified"}
            (proyecto / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
            df = pd.DataFrame({"id": range(101), "actividad": range(101), "plan": ["a", "b"] * 50 + ["a"], "Churn": [0] * 50 + [1] * 50 + [None]})
            with zipfile.ZipFile(raiz / "fuente.zip", "w") as z:
                z.writestr("datos.csv", df.to_csv(index=False))
            resumen = preparar(proyecto)
            self.assertEqual(resumen.filas.sum(), 100)
            info = json.loads((proyecto / "reports/preparacion/preparacion.json").read_text(encoding="utf-8"))
            self.assertEqual(info["fuentes"][0]["filas_sin_target"], 1)
            self.assertEqual(info["ids_compartidos_train_test"], 0)
            baseline(proyecto)
            entrenar(proyecto)
            texto = evaluar(proyecto)
            self.assertIn("baseline", texto)
            final = json.loads((proyecto / "reports/evaluacion/evaluacion_test.json").read_text(encoding="utf-8"))
            self.assertEqual(final["modelo"]["casos"], len(cargar(proyecto, "test")))
            self.assertEqual(len(final["modelo"]["matriz_confusion"]), 2)

    def test_particion_temporal_conserva_el_orden(self):
        with TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporal:
            raiz = Path(temporal)
            proyecto = raiz / "temporal"
            proyecto.mkdir()
            cfg = {"target": "Churn", "id": "id", "date": "fecha", "exclude": ["id", "fecha"], "source_zip": "../fuente.zip", "members": {"full": "datos.csv"}, "split": "temporal"}
            (proyecto / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
            df = pd.DataFrame({"id": [1, 2] * 4, "fecha": [f"2025-0{i}-01" for i in range(1, 5) for _ in range(2)], "Churn": [0, 1] * 4})
            with zipfile.ZipFile(raiz / "fuente.zip", "w") as z:
                z.writestr("datos.csv", df.to_csv(index=False))
            preparar(proyecto)
            train, valid, test = [cargar(proyecto, p) for p in ["train", "valid", "test"]]
            self.assertLess(train.fecha.max(), valid.fecha.min())
            self.assertLess(valid.fecha.max(), test.fecha.min())


if __name__ == "__main__":
    unittest.main()
