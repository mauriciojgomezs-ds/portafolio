from pathlib import Path
import sys,unittest,itertools
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from workforce_scheduling.balance import solve_balanced
from workforce_scheduling.analysis import audit_plan

class BalanceTests(unittest.TestCase):
    def test_coincide_con_enumeracion_y_respeta_tope(self):
        e=pd.DataFrame({'employee':['A','B','C'],'hourly_cost_units':[10.,12.,11.],'unavailable_day':[2,2,3]})
        patterns=pd.DataFrame([['A',0,0,6,3,8,80.],['B',0,0,6,3,8,96.],['C',0,4,10,7,8,88.]],columns=['employee','day','start_slot','lunch_slot','break_slot','paid_hours','cost_units'])
        d=pd.DataFrame([(day,slot,int(day==0 and slot in [0,19])) for day in range(7) for slot in range(20)],columns=['day','slot','required_agents'])
        prefs=pd.DataFrame({'employee':['A','B','C'],'preferred_start_slot':[0,0,4]})
        cfg={'max_weekly_hours':40,'max_consecutive_days':4,'solver_time_limit_seconds':10,'solver_relative_gap':0,'balanced_extra_cost_ratio':.6,'balance_hours_weight':1.,'preference_miss_weight':.25}
        objectives=[]
        for flags in itertools.product([0,1],repeat=3):
            p=patterns.loc[np.array(flags,dtype=bool)];check=audit_plan(p,d,e,cfg)
            if check.get('cobertura_completa') and check['coste_unidades']<=168*1.6:
                hours=p.groupby('employee').paid_hours.sum().reindex(e.employee,fill_value=0);objectives.append(float(hours.max()-hours.min()))
        plan,info=solve_balanced(patterns,d,e,prefs,cfg,168)
        self.assertEqual(info['objetivo_puntuacion'],min(objectives));self.assertTrue(info['cobertura_completa']);self.assertLessEqual(info['coste_unidades'],168*1.6)
        self.assertEqual(len(plan),3)
    def test_preferencias_incompletas_se_rechazan(self):
        e=pd.DataFrame({'employee':['A']});prefs=pd.DataFrame({'employee':[],'preferred_start_slot':[]})
        with self.assertRaises(ValueError):solve_balanced(pd.DataFrame(),pd.DataFrame(),e,prefs,{},0)
