from pathlib import Path
import json
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from industrial_anomaly_detection.informe import generar_informe, comparison, atomic

class InformeTest(unittest.TestCase):
    def test_fallo_con_resultados_anteriores_no_se_presenta_como_completado(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            p=Path(folder)
            atomic(p/'reports/ejecucion/resumen.json', json.dumps({'estado':'error'}))
            atomic(p/'reports/evaluacion/evaluacion.json', json.dumps({'modelo':{'accuracy':0.9}}))
            generar_informe(p)
            result=json.loads((p/'reports/informe_final/informe_final.json').read_text(encoding='utf-8'))
            self.assertEqual(result['estado'],'ejecucion_no_completada')
            text=(p/'reports/informe_final/informe_final.md').read_text(encoding='utf-8')
            self.assertIn('pasada anterior',text)
            self.assertIn('preparacion',result['etapas_sin_reporte'])

    def test_comparacion_respeta_direccion_y_datos_ausentes(self):
        results={'baseline':{'mae':2.0},'modelo':{'mae':3.0}}
        self.assertIn('no mejora', comparison(results,'forecast'))
        self.assertEqual(comparison({'baseline':{'f1':None},'modelo':{'f1':0.1}},'anomaly'),'')
        self.assertIn('no demuestran', comparison({'baseline':{},'modelo':{}},'music_content'))

    def test_manifiesto_identifica_artefactos_y_huellas(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            p=Path(folder)
            atomic(p/'reports/eda/eda.json',json.dumps({'filas':17}))
            generar_informe(p)
            result=json.loads((p/'reports/informe_final/informe_final.json').read_text(encoding='utf-8'))
            source=next(s for s in result['fuentes'] if s['ruta']=='reports/eda/eda.json')
            self.assertEqual(len(source['sha256']),64)
            self.assertEqual(result['resultados']['eda']['filas'],17)
            self.assertEqual(result['estado'],'ejecucion_no_completada')
