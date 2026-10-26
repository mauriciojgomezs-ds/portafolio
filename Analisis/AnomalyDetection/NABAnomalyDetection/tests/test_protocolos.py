import unittest
import sys
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from nab_anomaly_detection.temporal import causal_scores

class ProtocolosTest(unittest.TestCase):

    def test_future_change_does_not_modify_past_anomaly_scores(self):
            original = pd.DataFrame({'value':np.arange(100,dtype=float)})
            altered = original.copy()
            altered.loc[70:,'value'] = 10000
            pd.testing.assert_series_equal(causal_scores(original,10).iloc[:70],causal_scores(altered,10).iloc[:70])

if __name__=="__main__":
    unittest.main()
