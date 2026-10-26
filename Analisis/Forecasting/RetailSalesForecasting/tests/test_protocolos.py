import unittest
import sys
from pathlib import Path
import json
from tempfile import TemporaryDirectory
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from retail_sales_forecasting.temporal import forecast_features
from retail_sales_forecasting.data import retail_clean

class ProtocolosTest(unittest.TestCase):

    def test_current_target_not_present_in_its_own_forecast_lags(self):
            frame = pd.DataFrame({'timestamp':pd.date_range('2020-01-05',periods=12,freq='W'),'value':np.arange(12,dtype=float)})
            changed = frame.copy()
            changed.loc[8,'value'] = 9000
            columns = ['lag_1','lag_2','lag_3','lag_4','media_4']
            before = forecast_features(frame).set_index('timestamp')
            after = forecast_features(changed).set_index('timestamp')
            pd.testing.assert_series_equal(before.loc[frame.loc[8,'timestamp'],columns],after.loc[frame.loc[8,'timestamp'],columns])

    def test_returns_and_missing_customers_have_distinct_policies(self):
            frame = pd.DataFrame({'InvoiceNo':['1','C2','3','4'],'InvoiceDate':['2020-01-01']*4,'Quantity':[2,-1,1,1],'UnitPrice':[5,5,0,3],'CustomerID':[1,1,1,None]})
            clean = retail_clean(frame)
            self.assertEqual(clean.amount.sum(),13)
            self.assertEqual(len(clean),2)
            # El pronóstico incluye compras anónimas; RFM las retira posteriormente.
            self.assertEqual(clean.CustomerID.isna().sum(),1)

if __name__=="__main__":
    unittest.main()
