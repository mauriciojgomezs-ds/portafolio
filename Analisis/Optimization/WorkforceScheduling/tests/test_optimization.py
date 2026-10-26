from pathlib import Path
import sys,unittest,itertools
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from workforce_scheduling.analysis import audit_plan,solve,coverage_matrix

class OptimizationTest(unittest.TestCase):
    def setUp(self):
        self.cfg={'max_weekly_hours':40,'max_consecutive_days':4,'solver_time_limit_seconds':10,'solver_relative_gap':0}
        self.employees=pd.DataFrame({'employee':['A','B','C'],'hourly_cost_units':[10.,12.,11.],'unavailable_day':[2,2,3]})
        self.patterns=pd.DataFrame([['A',0,0,6,3,8,80.,0],['B',0,0,6,3,8,96.,1],['C',0,4,10,7,8,88.,2]],columns=['employee','day','start_slot','lunch_slot','break_slot','paid_hours','cost_units','candidate_id'])
        self.demand=pd.DataFrame([(d,s,int(d==0 and s in [0,19])) for d in range(7) for s in range(20)],columns=['day','slot','required_agents'])

    def test_solver_coincide_con_enumeracion_completa(self):
        costs=[]
        for flags in itertools.product([0,1],repeat=3):
            plan=self.patterns.loc[np.array(flags,dtype=bool)];check=audit_plan(plan,self.demand,self.employees,self.cfg)
            if check.get('cobertura_completa'):costs.append(check['coste_unidades'])
        plan,result=solve(self.patterns,self.demand,self.employees,self.cfg)
        self.assertEqual(result['objetivo_coste'],min(costs));self.assertEqual(result['objetivo_coste'],168.)
        self.assertTrue(audit_plan(plan,self.demand,self.employees,self.cfg)['cobertura_completa'])

    def test_descansos_no_aportan_cobertura(self):
        coverage=coverage_matrix(self.patterns.iloc[:1]).sum(axis=1)
        self.assertEqual(coverage[3],0);self.assertEqual(coverage[6],0);self.assertEqual(coverage.sum(),14)

    def test_auditoria_detecta_doble_turno_y_disponibilidad(self):
        duplicate=pd.concat([self.patterns.iloc[:1]]*2)
        self.assertIn('mas_de_un_turno_diario',audit_plan(duplicate,self.demand,self.employees,self.cfg)['errores'])
        unavailable=self.patterns.iloc[:1].assign(day=2)
        self.assertIn('disponibilidad',audit_plan(unavailable,self.demand,self.employees,self.cfg)['errores'])

    def test_cobertura_incompleta_no_es_solucion_factible(self):
        check=audit_plan(self.patterns.iloc[:1],self.demand,self.employees,self.cfg)
        self.assertTrue(check['restricciones_laborales_cumplidas']);self.assertFalse(check['cobertura_completa'])
