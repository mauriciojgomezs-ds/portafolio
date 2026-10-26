from pathlib import Path
import sys,unittest
import pandas as pd
from sklearn.metrics import adjusted_rand_score
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from email_community_analysis.analysis import validate,partition_frame

class GraphTests(unittest.TestCase):
    def test_particion_conserva_aislado(self):
        frame=partition_frame([0,1,2],[{0,1},{2}])
        self.assertEqual(len(frame),3);self.assertEqual(frame.loc[frame.node.eq(2),'community'].iloc[0],1)
    def test_comunidad_solapada_se_rechaza(self):
        with self.assertRaises(ValueError):partition_frame([0,1,2],[{0,1},{1,2}])
    def test_arista_sin_etiqueta_se_rechaza(self):
        with self.assertRaises(ValueError):validate(pd.DataFrame({'source':[0],'target':[2]}),pd.DataFrame({'node':[0,1],'department':[0,0]}))
    def test_ari_no_depende_del_numero_de_etiqueta(self):
        a=partition_frame([0,1,2],[{0,1},{2}]);b=[7,7,9]
        self.assertEqual(adjusted_rand_score(a.community,b),1.)
