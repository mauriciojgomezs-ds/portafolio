from pathlib import Path
import sys,unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from telecom_churn.decisiones import split_calibration,reliability,threshold_table,decision_metrics

class DecisionTests(unittest.TestCase):
    def test_separacion_por_cliente(self):
        df=pd.DataFrame({'id':np.repeat(range(40),2),'target':np.tile([0,1],40)})
        fit,cal,_=split_calibration(df,{'split':'provided','id':'id','target':'target'})
        self.assertFalse(set(fit.id)&set(cal.id));self.assertEqual(len(fit)+len(cal),len(df))
    def test_calibracion_temporal_no_usa_fechas_futuras(self):
        df=pd.DataFrame({'date':np.repeat(pd.date_range('2020-01-01',periods=3),2),'target':[0,1]*3})
        fit,cal,_=split_calibration(df,{'split':'temporal','date':'date','target':'target'})
        self.assertLess(fit.date.max(),cal.date.min())
    def test_fiabilidad_incluye_probabilidad_uno_y_soporte(self):
        frame,ece=reliability([0,1,1],[0,1,1]);self.assertEqual(frame.casos.sum(),3);self.assertEqual(ece,0);self.assertEqual(frame.iloc[-1]['bin'],9)
    def test_umbral_costes_y_politica_ninguno(self):
        table,threshold=threshold_table([0,1],[.8,.2],5,1)
        selected=decision_metrics([0,1],[.8,.2],threshold,5,1)
        self.assertEqual(selected['coste_error_total'],1);self.assertEqual(selected['priorizados'],2)
        self.assertEqual(decision_metrics([1],[1.],np.nextafter(1.,2.),5,1)['priorizados'],0)
