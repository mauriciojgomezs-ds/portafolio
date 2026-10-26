from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from call_center_staffing.analysis import service_level, staffing, calendar

class StaffingTest(unittest.TestCase):
    def setUp(self):
        self.cfg={'interval_minutes':30,'target_wait_seconds':20,'target_service_level':.8,'max_occupancy':.85,'shrinkage':.3}

    def test_erlang_c_caso_analitico_un_agente(self):
        # M/M/1: a=0.5; P(espera)=rho=0.5. En t=0, SL=1-rho.
        self.assertAlmostEqual(service_level(3,300,1,1800,0),.5)
        self.assertAlmostEqual(service_level(3,300,1,1800,20),1-.5*np.exp(-.5*20/300))
        self.assertEqual(service_level(6,300,1,1800,20),0)

    def test_dotacion_cubre_servicio_ocupacion_y_shrinkage(self):
        previous=0
        for calls in [0,1,3,10,50,100]:
            net,gross=staffing(calls,300,self.cfg)
            self.assertGreaterEqual(net,previous);previous=net
            self.assertGreaterEqual(service_level(calls,300,net,1800,20),.8)
            if calls:
                self.assertLessEqual(calls*300/1800/net,.85)
                self.assertEqual(gross,int(np.ceil(net/.7)))
        self.assertEqual(staffing(0,300,self.cfg),(0,0))

    def test_atributos_no_dependen_de_volumen_futuro(self):
        frame=pd.DataFrame({'timestamp':pd.date_range('2021-03-01 09:00',periods=4,freq='30min'),'value':[1,2,3,4]})
        changed=frame.assign(value=[1000,0,9999,500])
        np.testing.assert_array_equal(calendar(frame),calendar(changed))

    def test_parametros_invalidos_no_producen_dotacion(self):
        with self.assertRaises(ValueError):staffing(10,300,{**self.cfg,'shrinkage':1})
        with self.assertRaises(ValueError):service_level(1,0,1,1800,20)
