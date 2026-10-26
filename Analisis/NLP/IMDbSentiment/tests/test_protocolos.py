import unittest
import sys
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from imdb_sentiment.data import text_partitions

class ProtocolosTest(unittest.TestCase):

    def test_external_test_overlap_removed_from_train(self):
            train = pd.DataFrame({'text':[f'Reseña {i}' for i in range(100)],'label':[i%2 for i in range(100)]})
            test = pd.DataFrame({'text':['<br>RESEÑA   0','Texto externo'],'label':[0,1]})
            parts = text_partitions(train,supplied_test=test)
            self.assertEqual(len(parts['test']),2)
            self.assertFalse(set(parts['test'].text_key) & set(parts['train'].text_key))
            self.assertFalse(set(parts['test'].text_key) & set(parts['valid'].text_key))

if __name__=="__main__":
    unittest.main()
