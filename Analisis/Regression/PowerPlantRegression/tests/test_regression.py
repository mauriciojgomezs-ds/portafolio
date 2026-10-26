from pathlib import Path
import sys,unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from power_plant_regression.analysis import FEATURES,grouped_split,conformal_quantile,x

class RegressionTest(unittest.TestCase):
    def test_condiciones_identicas_no_cruzan_particiones(self):
        rng=np.random.default_rng(42);data=pd.DataFrame(rng.normal(size=(100,len(FEATURES))),columns=FEATURES)
        data=pd.concat([data,data],ignore_index=True);data['PE']=np.arange(200)
        parts=grouped_split(data,42);groups=[set(map(tuple,data.iloc[idx][FEATURES].to_numpy())) for idx in parts.values()]
        for i in range(len(groups)):
            for j in range(i+1,len(groups)):self.assertFalse(groups[i]&groups[j])
        self.assertEqual(sum(map(len,parts.values())),len(data))

    def test_cuantil_conformal_corrige_tamano_finito(self):
        self.assertEqual(conformal_quantile(np.arange(1,10),.2),8.)
        with self.assertRaises(ValueError):conformal_quantile(np.arange(1,10),.05)
        with self.assertRaises(ValueError):conformal_quantile([1,-1],.2)

    def test_objetivo_e_id_no_entran_a_prediccion(self):
        df=pd.DataFrame({f:[1.,2.] for f in FEATURES});df['PE']=[400,500];df['source_id']=[1,2]
        np.testing.assert_array_equal(x(df),x(df.assign(PE=[999,888],source_id=[99,88])))
