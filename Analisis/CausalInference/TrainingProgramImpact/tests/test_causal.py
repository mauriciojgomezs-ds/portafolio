from pathlib import Path
import sys,unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from training_program_impact.analysis import difference,adjusted,bootstrap,PRE

class CausalTest(unittest.TestCase):
    def test_diferencia_contraste_y_intervalo(self):
        df=pd.DataFrame({'treatment':[0,0,1,1],'re78':[1.,3.,4.,6.]})
        result=difference(df)
        self.assertAlmostEqual(result['efecto_usd'],3.)
        self.assertAlmostEqual(result['error_estandar'],np.sqrt(2.))
        self.assertLess(result['ci_inferior'],result['efecto_usd'])
        self.assertGreater(result['ci_superior'],result['efecto_usd'])

    def test_ajuste_recupera_efecto_lineal_y_no_usa_futuro(self):
        rng=np.random.default_rng(21);n=200
        df=pd.DataFrame(rng.normal(size=(n,len(PRE))),columns=PRE)
        df['treatment']=np.tile([0,1],n//2)
        df['re78']=100+7*df.treatment+df[PRE].to_numpy()@np.arange(1,9)
        result=adjusted(df)
        self.assertAlmostEqual(result['efecto_usd'],7.,places=9)
        self.assertNotIn('re78',result['covariables'])
        with self.assertRaises(ValueError):adjusted(df.assign(re74=0))

    def test_bootstrap_es_reproducible_y_preserva_brazos(self):
        rng=np.random.default_rng(19);df=pd.DataFrame(rng.normal(size=(160,len(PRE))),columns=PRE);df['treatment']=np.tile([0,1],80);df['re78']=500+30*df.treatment+rng.normal(size=160)
        a=bootstrap(df,10,42,.95);b=bootstrap(df,10,42,.95)
        np.testing.assert_array_equal(a,b);self.assertEqual(a.shape,(10,2))
