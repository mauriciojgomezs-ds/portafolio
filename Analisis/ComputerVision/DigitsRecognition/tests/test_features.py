from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from digits_recognition.analysis import features, metrics

class FeatureTest(unittest.TestCase):
    def test_atributos_no_dependen_de_otras_imagenes(self):
        images=np.arange(128,dtype=np.float32).reshape(2,8,8)%17
        np.testing.assert_allclose(features(images)[:1],features(images[:1]))
        self.assertEqual(features(images).shape,(2,192))
        self.assertTrue(np.isfinite(features(images)).all())

    def test_macro_incluye_clases_omitidas_en_prediccion(self):
        result=metrics(np.arange(10),np.zeros(10,dtype=int))
        self.assertAlmostEqual(result['accuracy'],.1)
        self.assertLess(result['f1_macro'],.1)
        self.assertEqual(len(result['matriz_confusion']),10)
