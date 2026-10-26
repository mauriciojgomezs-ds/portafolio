from pathlib import Path
import sys
import unittest
import tempfile
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from retail_kpi_analysis.analysis import clean, aggregate, monthly

class KPITest(unittest.TestCase):
    def test_codigos_mixtos_se_guardan_sin_perder_cancelaciones(self):
        frame=pd.DataFrame([[536365,85123,'2021-01-01',2,10,1,'UK'],['C536365','85123A','2021-01-02',-1,10,1,'UK']],columns=['InvoiceNo','StockCode','InvoiceDate','Quantity','UnitPrice','CustomerID','Country'])
        cleaned,_=clean(frame)
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path=Path(folder)/'detail.parquet';cleaned.to_parquet(path,index=False)
            restored=pd.read_parquet(path)
        self.assertEqual(restored.InvoiceNo.tolist(),['536365','C536365'])
        self.assertEqual(restored.is_cancellation.tolist(),[False,True])
        self.assertEqual(aggregate(restored)['facturacion_neta'],10)

    def test_ajustes_y_cliente_ausente_preservan_facturacion(self):
        rows=[['A', '2021-01-01',2,100,None,'UK'],['C-A','2021-01-31',-1,50,1,'UK'],['B','2021-02-03',1,0,2,'UK']]
        frame=pd.DataFrame(rows+[rows[0]],columns=['InvoiceNo','InvoiceDate','Quantity','UnitPrice','CustomerID','Country'])
        cleaned,info=clean(frame);result=aggregate(cleaned)
        self.assertEqual(info['duplicados_retirados'],1)
        self.assertEqual(info['filas_invalidas_retiradas'],1)
        self.assertEqual(result['facturacion_positiva'],200)
        self.assertEqual(result['ajustes_negativos_absolutos'],50)
        self.assertEqual(result['facturacion_neta'],150)
        self.assertEqual(result['filas_sin_cliente'],1)
        self.assertEqual(result['reconciliacion_gbp'],0)

    def test_mes_parcial_y_reconciliacion_de_agregados(self):
        frame=pd.DataFrame([['A','2021-01-01',2,100,1,'UK'],['C-A','2021-01-31',-1,50,1,'UK'],['B','2021-02-03',1,20,2,'FR']],columns=['InvoiceNo','InvoiceDate','Quantity','UnitPrice','CustomerID','Country'])
        cleaned,_=clean(frame);m=monthly(cleaned)
        self.assertEqual(m.mes_completo_por_cobertura.tolist(),[True,False])
        self.assertEqual(m.facturacion_neta.sum(),aggregate(cleaned)['facturacion_neta'])
