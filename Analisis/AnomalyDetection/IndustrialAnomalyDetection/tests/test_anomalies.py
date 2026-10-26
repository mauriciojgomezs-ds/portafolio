from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from industrial_anomaly_detection.analysis import FEATURES, EXCLUDED, x, metrics

class AnomalyTest(unittest.TestCase):
    def test_etiquetas_e_ids_no_entran_al_detector(self):
        frame=pd.DataFrame({f:[1.,2.] for f in FEATURES})
        frame['label']=[0,1];frame['TWF']=[0,1];frame['source_id']=[1,2]
        changed=frame.assign(label=[1,0],TWF=[1,0],source_id=[999,888])
        np.testing.assert_array_equal(x(frame),x(changed))
        self.assertFalse(set(FEATURES)&set(EXCLUDED))

    def test_sin_alertas_no_oculta_fallos(self):
        result=metrics(np.array([0,0,1]),np.array([.1,.2,.3]),1.)
        self.assertEqual(result['precision'],0)
        self.assertEqual(result['recall'],0)
        self.assertEqual(result['fallos_reales'],1)
        self.assertEqual(result['matriz_confusion'],[[2,0],[1,0]])
