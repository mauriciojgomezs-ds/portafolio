from pathlib import Path
import sys,unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from customer_return_survival.analysis import build_cohort,concordance,bootstrap_concordance

class SurvivalTests(unittest.TestCase):
    def raw(self):
        start=pd.Timestamp('2020-01-01')
        rows=[('A',0,'1','x',2,10),('A',0,'2','y',1,5),('A',10,'3','x',100,100),('B',20,'4','x',1,3),('C',100,'5','x',1,4)]
        return pd.DataFrame([{'CustomerID':c,'InvoiceDate':start+pd.Timedelta(days=d),'InvoiceNo':i,'StockCode':s,'Quantity':q,'UnitPrice':p,'Country':'United Kingdom'} for c,d,i,s,q,p in rows])
    def test_evento_censura_y_sin_seguimiento(self):
        frame,meta=build_cohort(self.raw(),90);frame=frame.set_index('customer_id')
        self.assertEqual(frame.loc['A','duration_days'],10);self.assertEqual(frame.loc['A','event'],1)
        self.assertEqual(frame.loc['B','duration_days'],80);self.assertEqual(frame.loc['B','event'],0);self.assertEqual(meta['clientes_sin_seguimiento_excluidos'],1)
        self.assertAlmostEqual(frame.loc['A','log_basket_gbp'],np.log1p(25));self.assertAlmostEqual(frame.loc['A','log_items'],np.log1p(2))
    def test_compra_despues_del_horizonte_no_es_evento(self):
        raw=self.raw();raw.loc[2,'InvoiceDate']=raw.InvoiceDate.min()+pd.Timedelta(days=95)
        frame,_=build_cohort(raw,90);a=frame.set_index('customer_id').loc['A'];self.assertEqual(a.event,0);self.assertEqual(a.duration_days,90)
    def test_features_no_cambian_con_importe_futuro(self):
        a,_=build_cohort(self.raw(),90);raw=self.raw();raw.loc[2,'UnitPrice']=1e6;b,_=build_cohort(raw,90)
        np.testing.assert_array_equal(a[['log_basket_gbp','log_items','uk']],b[['log_basket_gbp','log_items','uk']])
    def test_signo_concordancia_y_bootstrap_reproducible(self):
        df=pd.DataFrame({'duration_days':range(1,31),'event':np.ones(30,dtype=int)});risk=-df.duration_days.to_numpy()
        self.assertEqual(concordance(df,risk),1.);self.assertEqual(concordance(df,np.ones(30)),.5)
        self.assertEqual(bootstrap_concordance(df,risk,42,10),bootstrap_concordance(df,risk,42,10))
