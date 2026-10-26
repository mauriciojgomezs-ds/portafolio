import unittest
import sys
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from netflix_genre_classification.data import text_partitions
from netflix_genre_classification.text import targets

class ProtocolosTest(unittest.TestCase):

    def test_title_groups_kept_together(self):
            frame = pd.DataFrame({'text':[f'Sinopsis distinta {i}' for i in range(120)],'title_key':[f'titulo {i//2}' for i in range(120)]})
            parts = text_partitions(frame,groups='title_key')
            for a,b in [('train','valid'),('train','test'),('valid','test')]:
                self.assertFalse(set(parts[a].title_key) & set(parts[b].title_key))

    def test_unseen_labels_are_counted(self):
            y, unseen = targets(pd.DataFrame({'labels':[['drama','unknown'],['unknown']]}),['drama'])
            self.assertEqual(unseen,2)
            self.assertEqual(y.tolist(),[[1],[0]])

if __name__=="__main__":
    unittest.main()
