import unittest
import sys
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from movielens_recommender.collaborative import recommend_ids

class ProtocolosTest(unittest.TestCase):

    def test_recommendation_excludes_seen_and_zero_signal(self):
            bundle = {'user_index':{198:0},'movies':[10,20,30],'popularity':np.array([100.,2.,0.]),'seen':csr_matrix([[1,0,0]])}
            self.assertEqual(recommend_ids(bundle,198,None,10),[20])

if __name__=="__main__":
    unittest.main()
