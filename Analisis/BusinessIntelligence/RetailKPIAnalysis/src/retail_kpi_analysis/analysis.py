"""KPIs reconciliables de facturación y devoluciones; análisis descriptivo de BI."""
from pathlib import Path
from urllib.request import urlopen
import shutil
import zipfile
import io
import html
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import config, report, report_path, save_frame, load_frame, sha256, write_json, read_json

def setup(project):
    path=Path(project)/config(project)['source']
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True);partial=path.with_suffix('.part')
        try:
            with urlopen('https://archive.ics.uci.edu/static/public/352/online+retail.zip',timeout=90) as src,partial.open('wb') as dst:shutil.copyfileobj(src,dst)
            with zipfile.ZipFile(partial) as z:
                if z.testzip() is not None or 'Online Retail.xlsx' not in z.namelist():raise ValueError('Fuente UCI inesperada o corrupta')
            partial.replace(path)
        finally:
            if partial.exists():partial.unlink()
    return path

def clean(df):
    original=len(df);df=df.copy()
    # Excel combina números y códigos como C536379: son identificadores, no magnitudes.
    for column in ['InvoiceNo','StockCode']:
        if column in df:df[column]=df[column].astype('string')
    df=df.drop_duplicates().copy();duplicates=original-len(df)
    df['InvoiceDate']=pd.to_datetime(df.InvoiceDate,errors='coerce')
    df['Quantity']=pd.to_numeric(df.Quantity,errors='coerce');df['UnitPrice']=pd.to_numeric(df.UnitPrice,errors='coerce')
    valid=df.InvoiceDate.notna()&np.isfinite(df.Quantity)&np.isfinite(df.UnitPrice)&df.UnitPrice.gt(0)&df.Quantity.ne(0)
    df=df[valid].copy();df['amount']=df.Quantity*df.UnitPrice
    df['month']=df.InvoiceDate.dt.to_period('M').astype(str)
    df['is_cancellation']=df.InvoiceNo.astype(str).str.upper().str.startswith('C')
    return df,{'filas_originales':original,'duplicados_retirados':duplicates,'filas_invalidas_retiradas':original-duplicates-len(df),'filas_preparadas':len(df)}

def aggregate(df):
    gross=float(df.loc[df.amount.gt(0),'amount'].sum());returns=float(-df.loc[df.amount.lt(0),'amount'].sum());net=float(df.amount.sum())
    invoices=df.loc[df.amount.gt(0)].groupby('InvoiceNo').amount.sum()
    return {'moneda':'GBP','facturacion_positiva':gross,'ajustes_negativos_absolutos':returns,'facturacion_neta':net,'ratio_ajustes_sobre_positiva':returns/gross if gross else None,'facturas_positivas':len(invoices),'ticket_medio_factura_positiva':float(invoices.mean()) if len(invoices) else None,'clientes_identificados':int(df.CustomerID.nunique()),'filas_sin_cliente':int(df.CustomerID.isna().sum()),'reconciliacion_gbp':gross-returns-net}

def monthly(df):
    out=[]
    low,high=df.InvoiceDate.min().normalize(),df.InvoiceDate.max().normalize()
    for month,group in df.groupby('month'):
        period=pd.Period(month,freq='M');complete=low<=period.start_time and high>=period.end_time.normalize()
        out.append({'mes':month,'mes_completo_por_cobertura':complete,**aggregate(group)})
    return pd.DataFrame(out)

def prepare(project):
    path=setup(project)
    with zipfile.ZipFile(path) as z:df=pd.read_excel(io.BytesIO(z.read('Online Retail.xlsx')),engine='openpyxl')
    df,info=clean(df);save_frame(project,df)
    info.update(sha256=sha256(path),fecha_min=str(df.InvoiceDate.min()),fecha_max=str(df.InvoiceDate.max()),cancelaciones_con_importe_positivo=int((df.is_cancellation&df.amount.gt(0)).sum()),moneda='GBP')
    return report(project,'preparacion',info,f"Se conservan **{len(df):,} líneas válidas** después de retirar duplicados exactos, fechas/cantidades inválidas, precios no positivos y cantidades cero. Los ajustes negativos se mantienen; importes positivos y negativos se clasifican por signo. La moneda de la fuente es GBP. Los IDs de cliente faltantes permanecen en el análisis de facturación y se excluyen solo de recuentos de clientes.")

def explore(project):
    df=load_frame(project);m=monthly(df)
    fig,ax=plt.subplots(figsize=(10,4));ax.plot(m.mes,m.facturacion_positiva,label='Positiva');ax.plot(m.mes,m.facturacion_neta,label='Neta');ax.tick_params(axis='x',rotation=60);ax.set(ylabel='GBP',title='Facturación mensual; revisar meses parciales');ax.legend();fig.tight_layout();fig.savefig(report_path(project,'eda','eda.png'),dpi=130);plt.close(fig)
    info={'filas':len(df),'paises':int(df.Country.nunique()),'meses':len(m),'meses_parciales':m.loc[~m.mes_completo_por_cobertura,'mes'].tolist(),'sin_cliente':int(df.CustomerID.isna().sum())}
    return report(project,'eda',info,f"La cobertura incluye **{len(m)} meses** y **{info['paises']} países**. Meses parciales según extremos observados: **{', '.join(info['meses_parciales']) or 'ninguno'}**. Los totales parciales no deben compararse directamente con meses completos. La cobertura de fechas tampoco garantiza integridad de la operación.")

def baseline(project):
    m=monthly(load_frame(project));complete=m[m.mes_completo_por_cobertura]
    if len(complete)<2:raise ValueError('Se necesitan dos meses completos para una referencia mensual')
    previous,last=complete.iloc[-2],complete.iloc[-1]
    info={'mes_referencia':previous.mes,'mes_analizado':last.mes,'neta_referencia_gbp':float(previous.facturacion_neta),'neta_analizada_gbp':float(last.facturacion_neta),'variacion_neta':float(last.facturacion_neta/previous.facturacion_neta-1) if previous.facturacion_neta else None}
    variation=f"{info['variacion_neta']:.2%}" if info['variacion_neta'] is not None else 'no definida: referencia igual a cero'
    return report(project,'baseline',info,f"Referencia descriptiva: **{previous.mes} → {last.mes}**, los últimos dos meses completos por cobertura. La variación de facturación neta es **{variation}**. No es un baseline predictivo ni demuestra una causa del cambio.")

def train(project):
    df=load_frame(project);m=monthly(df);country=df.groupby('Country').amount.sum().sort_values(ascending=False).rename('facturacion_neta').reset_index()
    m.to_csv(report_path(project,'modelado','kpis_mensuales.csv'),index=False);country.to_csv(report_path(project,'modelado','kpis_paises.csv'),index=False)
    kpi=aggregate(df);write_json(report_path(project,'modelado','indicadores.json'),kpi)
    # Dashboard offline, sin cuentas ni dependencias externas, con filtros de tabla.
    cards=''.join(f'<article><h2>{html.escape(name)}</h2><strong>{val:,.2f} GBP</strong></article>' for name,val in [('Positiva',kpi['facturacion_positiva']),('Ajustes negativos',kpi['ajustes_negativos_absolutos']),('Neta',kpi['facturacion_neta'])])
    doc='<!doctype html><html lang="es"><meta charset="utf-8"><title>Retail · Indicadores</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px;background:#f4f6fa;color:#162338}.cards{display:flex;gap:20px}article{background:white;padding:20px;border-radius:12px;flex:1}table{border-collapse:collapse;width:100%;background:white;margin:20px 0}th,td{padding:8px;border-bottom:1px solid #ddd;text-align:right}input{padding:10px;width:90%}</style><h1>Retail · Facturación y ajustes</h1><p>GBP · Importes facturados; no beneficios. Meses parciales identificados en la tabla.</p><div class="cards">'+cards+'</div><h2>Evolución mensual</h2>'+m.to_html(index=False,float_format=lambda v:f'{v:,.2f}',escape=True)+'<h2>Países</h2><label>Filtrar país <input id="search" placeholder="Escribe un país"></label>'+country.to_html(index=False,table_id='countries',float_format=lambda v:f'{v:,.2f}',escape=True)+'<script>document.getElementById("search").oninput=function(){for(const r of document.querySelectorAll("#countries tbody tr")){r.hidden=!r.textContent.toLowerCase().includes(this.value.toLowerCase())}}</script></html>'
    report_path(project,'modelado','dashboard.html').write_text(doc,encoding='utf-8')
    return report(project,'modelado',kpi,'Se construye un **modelo de indicadores y tablas agregadas**, no un modelo de machine learning. El dashboard local muestra facturación positiva, ajustes negativos y neta, con detalle mensual y filtro de países. Los ajustes se contabilizan en su fecha de factura; no se enlazan al pedido original ni se calculan beneficios.')

def evaluate(project):
    df=load_frame(project);kpi=aggregate(df);m=pd.read_csv(report_path(project,'modelado','kpis_mensuales.csv'));c=pd.read_csv(report_path(project,'modelado','kpis_paises.csv'))
    monthly_delta=float(m.facturacion_neta.sum()-kpi['facturacion_neta']);country_delta=float(c.facturacion_neta.sum()-kpi['facturacion_neta'])
    if any(abs(v)>.01 for v in [kpi['reconciliacion_gbp'],monthly_delta,country_delta]):raise ValueError('Los agregados no reconcilian con el detalle')
    result={**kpi,'reconciliacion_mensual_gbp':monthly_delta,'reconciliacion_paises_gbp':country_delta,'controles_aprobados':True,'indicadores_descriptivos':True}
    report_path(project,'evaluacion','resumen_kpis.csv').write_text(pd.DataFrame([result]).to_csv(index=False),encoding='utf-8')
    return report(project,'evaluacion',result,f"Facturación neta: **{kpi['facturacion_neta']:,.2f} GBP** = positiva **{kpi['facturacion_positiva']:,.2f}** − ajustes negativos **{kpi['ajustes_negativos_absolutos']:,.2f}**. Los ajustes representan **{kpi['ratio_ajustes_sobre_positiva']:.2%}** de la positiva. Las tablas mensual y por país reconcilian con el detalle a un céntimo. Estos controles validan coherencia aritmética, no integridad de datos ni rentabilidad. [Abrir dashboard](../modelado/dashboard.html).")

def run_stage(project,stage):return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
