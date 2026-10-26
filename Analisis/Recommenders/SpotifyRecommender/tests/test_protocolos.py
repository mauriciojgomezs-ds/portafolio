import unittest
import sys
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from spotify_recommender.common import config

class ProtocolosTest(unittest.TestCase):
    def test_paquete_y_fuente_local(self):
        project=Path(__file__).resolve().parents[1]
        cfg=config(project)
        self.assertTrue((project/cfg['source']).is_file())
        self.assertTrue((project/'pyproject.toml').is_file())

if __name__=="__main__":
    unittest.main()
