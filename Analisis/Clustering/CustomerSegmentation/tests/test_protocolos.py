import unittest
import sys
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from customer_segmentation.data import retail_clean

class ProtocolosTest(unittest.TestCase):

    def test_returns_and_missing_customers_have_distinct_policies(self):
            frame = pd.DataFrame({'InvoiceNo':['1','C2','3','4'],'InvoiceDate':['2020-01-01']*4,'Quantity':[2,-1,1,1],'UnitPrice':[5,5,0,3],'CustomerID':[1,1,1,None]})
            clean = retail_clean(frame)
            self.assertEqual(clean.amount.sum(),13)
            self.assertEqual(len(clean),2)
            # El pronóstico incluye compras anónimas; RFM las retira posteriormente.
            self.assertEqual(clean.CustomerID.isna().sum(),1)

if __name__=="__main__":
    unittest.main()
