"""Planificación binaria de turnos con demanda exógena y restricciones explícitas."""
from pathlib import Path
import math
import numpy as np
import pandas as pd
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import csr_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import config,report,report_path,save_frame,load_frame,write_json,read_json,sha256

def setup(project):
    cfg=config(project);p=Path(project);demand=p/cfg['source'];employees=p/cfg['employees_source']
    if demand.exists()!=employees.exists():raise ValueError('Deben existir ambas entradas; no se mezclan datos propios con una simulación parcial')
    if not demand.exists():
        demand.parent.mkdir(parents=True,exist_ok=True)
        profile=np.array([3,3,4,4,4,5,5,6,6,6,6,6,5,5,4,4,4,4,3,3]);rows=[]
        for day in range(7):
            values=np.maximum(2,profile-(1 if day>=5 else 0));values[7:12]+=int(day==2)
            for slot,required in enumerate(values):rows.append({'day':day,'slot':slot,'required_agents':int(required)})
        pd.DataFrame(rows).to_csv(demand,index=False)
        pd.DataFrame([{'employee':f'E{i+1:02d}','hourly_cost_units':12+.4*i,'unavailable_day':i%7} for i in range(14)]).to_csv(employees,index=False)
        write_json(demand.parent/'scenario_origin.json',{'origen':'Escenario didáctico sintético; no datos de operación ni pronóstico','demand_generator':'Perfil fijo por media hora; pico adicional miércoles y menor carga fin de semana','employees':'14 empleados ficticios, costes en unidades monetarias arbitrarias','available_days':'Cada empleado tiene un día no disponible; restricciones semanales agregan descansos'})
    return demand

def validate_inputs(demand,employees,cfg):
    slots=(cfg['close_hour']-cfg['open_hour'])*60/cfg['interval_minutes']
    if slots!=20 or cfg['shift_hours']!=8 or cfg['interval_minutes']!=30:raise ValueError('Esta versión admite 20 franjas de 30 min y turnos de 8 h; adaptar patrones para otras configuraciones')
    expected={(d,s) for d in range(7) for s in range(20)}
    if set(zip(demand.day,demand.slot))!=expected or len(demand)!=140:raise ValueError('Demanda requiere una fila por cada día/franja')
    if not np.isfinite(demand.required_agents).all() or (demand.required_agents<0).any() or (demand.required_agents%1!=0).any():raise ValueError('Demanda debe ser un conteo entero no negativo')
    if employees.employee.duplicated().any() or employees.empty or not np.isfinite(employees.hourly_cost_units).all() or (employees.hourly_cost_units<=0).any():raise ValueError('Empleados y costes no válidos')
    if not employees.unavailable_day.isin(range(7)).all():raise ValueError('Disponibilidad no válida')
    if cfg['max_weekly_hours']<8 or not 1<=cfg['max_consecutive_days']<=7:raise ValueError('Restricciones semanales no válidas')

def prepare(project):
    cfg=config(project);path=setup(project);d=pd.read_csv(path).sort_values(['day','slot']).reset_index(drop=True);e=pd.read_csv(Path(project)/cfg['employees_source']);validate_inputs(d,e,cfg);save_frame(project,d,'demand');save_frame(project,e,'employees')
    origin_path=path.parent/'scenario_origin.json'
    origin=read_json(origin_path) if origin_path.exists() else {'origen':'Fuente local aportada; procedencia no verificada'}
    info={'origen':origin['origen'],'fuente_sha256':sha256(path),'empleados_sha256':sha256(Path(project)/cfg['employees_source']),'empleados':len(e),'intervalos':len(d),'demanda_agente_horas':float(d.required_agents.sum()*.5),'particiones':'No aplica: optimización de un escenario fijo, sin aprendizaje predictivo'}
    return report(project,'preparacion',info,f"Escenario de **{len(e)} empleados ficticios** y **{len(d)} franjas** de una semana hipotética. Demanda requerida: **{info['demanda_agente_horas']:.1f} agente-horas**. Las entradas son **sintéticas y locales**, claramente identificadas; no se generan pronósticos, llamadas ni requisitos mediante Erlang C. La optimización consume requisitos de cobertura ya definidos y no depende de otros proyectos.")

def explore(project):
    d=load_frame(project,'demand');matrix=d.required_agents.to_numpy().reshape(7,20);fig,ax=plt.subplots(figsize=(10,4));im=ax.imshow(matrix,aspect='auto',cmap='Blues');ax.set(xlabel='Franja de media hora desde 09:00',ylabel='Día: 0=lunes',title='Demanda exógena del escenario sintético');fig.colorbar(im,ax=ax,label='Agentes requeridos');fig.tight_layout();fig.savefig(report_path(project,'eda','eda.png'),dpi=130);plt.close(fig)
    info={'demanda_minima':int(d.required_agents.min()),'demanda_maxima':int(d.required_agents.max()),'agente_horas_requeridas':float(d.required_agents.sum()*.5)}
    return report(project,'eda',info,f"Cobertura requerida entre **{info['demanda_minima']} y {info['demanda_maxima']} agentes** por franja. Estos conteos son entradas del escenario, no estimaciones de volumen ni dotación calculada desde llamadas. Los costes son unidades monetarias arbitrarias; no se interpretan como salarios de un país.")

def candidates(employees):
    rows=[]
    for person in employees.itertuples():
        for day in range(7):
            if day==person.unavailable_day:continue
            for start in range(5):
                for lunch_offset in [6,7,8,9]:
                    for break_offset in [3,11]:rows.append({'employee':person.employee,'day':day,'start_slot':start,'lunch_slot':start+lunch_offset,'break_slot':start+break_offset,'paid_hours':8,'cost_units':float(8*person.hourly_cost_units)})
    out=pd.DataFrame(rows);out['candidate_id']=np.arange(len(out));return out

def coverage_matrix(patterns):
    a=np.zeros((140,len(patterns)))
    for j,row in enumerate(patterns.itertuples()):
        working=[s for s in range(row.start_slot,row.start_slot+16) if s not in (row.lunch_slot,row.break_slot)]
        a[np.array(working)+row.day*20,j]=1
    return a

def max_run(days):
    active=set(days);best=current=0
    for day in range(7):current=current+1 if day in active else 0;best=max(best,current)
    return best

def audit_plan(plan,demand,employees,cfg):
    errors=[];people=employees.set_index('employee')
    for row in plan.itertuples():
        if row.employee not in people.index:errors.append('empleado_desconocido');continue
        if row.day not in range(7) or row.day==people.loc[row.employee,'unavailable_day']:errors.append('disponibilidad')
        if row.start_slot not in range(5) or row.lunch_slot-row.start_slot not in [6,7,8,9] or row.break_slot-row.start_slot not in [3,11] or row.paid_hours!=8:errors.append('patron_descanso')
        if not math.isclose(row.cost_units,8*people.loc[row.employee,'hourly_cost_units'],abs_tol=1e-8):errors.append('coste_patron')
    if plan.duplicated(['employee','day']).any():errors.append('mas_de_un_turno_diario')
    for person,group in plan.groupby('employee'):
        if group.paid_hours.sum()>cfg['max_weekly_hours']:errors.append('horas_semanales')
        if max_run(group.day)>cfg['max_consecutive_days']:errors.append('dias_consecutivos')
    if errors:return {'restricciones_laborales_cumplidas':False,'errores':sorted(set(errors))}
    coverage=coverage_matrix(plan).sum(axis=1);need=demand.sort_values(['day','slot']).required_agents.to_numpy();deficit=np.maximum(0,need-coverage)
    return {'restricciones_laborales_cumplidas':True,'cobertura_completa':bool(np.all(deficit==0)),'deficit_agente_intervalos':float(deficit.sum()),'coste_unidades':float(plan.cost_units.sum()),'turnos':len(plan),'horas_pagadas':float(plan.paid_hours.sum()),'exceso_agente_horas':float(np.maximum(0,coverage-need).sum()*.5),'errores':[]}

def greedy(patterns,demand,cfg):
    a=coverage_matrix(patterns);need=demand.required_agents.to_numpy();coverage=np.zeros(140);selected=[];worked={}
    for day in range(7):
        while np.any(coverage[day*20:(day+1)*20]<need[day*20:(day+1)*20]):
            best=None;best_ratio=0
            for j in patterns.index[patterns.day.eq(day)]:
                row=patterns.loc[j];days=worked.get(row.employee,[])
                if day in days or (len(days)+1)*8>cfg['max_weekly_hours'] or max_run(days+[day])>cfg['max_consecutive_days']:continue
                gain=float(np.minimum(1,np.maximum(0,need-coverage))@a[:,j]);ratio=gain/row.cost_units
                if ratio>best_ratio:best=j;best_ratio=ratio
            if best is None:break
            row=patterns.loc[best];selected.append(best);worked.setdefault(row.employee,[]).append(day);coverage+=a[:,best]
    return patterns.loc[selected].reset_index(drop=True)

def baseline(project):
    cfg=config(project);d,e=load_frame(project,'demand'),load_frame(project,'employees');patterns=candidates(e);plan=greedy(patterns,d,cfg);(Path(project)/'models').mkdir(parents=True,exist_ok=True);plan.to_csv(Path(project)/'models/baseline_plan.csv',index=False);result=audit_plan(plan,d,e,cfg)
    if not result['restricciones_laborales_cumplidas']:raise ValueError('Baseline viola restricciones estructurales')
    state='cubre todas las franjas' if result['cobertura_completa'] else f"deja {result['deficit_agente_intervalos']:.0f} agente-intervalos sin cubrir"
    return report(project,'baseline',result,f"Heurística secuencial por día: asigna el patrón con mayor cobertura pendiente por coste, respetando disponibilidad, horas y días consecutivos. Coste **{result['coste_unidades']:,.2f} unidades**; **{state}**. Una solución incompleta no se considera una alternativa factible aunque su coste sea menor.")

def solve(patterns,demand,employees,cfg):
    cover=coverage_matrix(patterns);matrices=[cover];lower=list(demand.required_agents);upper=[np.inf]*140
    for employee in employees.employee:
        own=patterns.employee.eq(employee).to_numpy()
        for day in range(7):matrices.append((own&patterns.day.eq(day).to_numpy())[None,:].astype(float));lower.append(0);upper.append(1)
        matrices.append((own*patterns.paid_hours.to_numpy())[None,:]);lower.append(0);upper.append(cfg['max_weekly_hours'])
        window=cfg['max_consecutive_days']+1
        for start in range(8-window):matrices.append((own&patterns.day.between(start,start+window-1).to_numpy())[None,:].astype(float));lower.append(0);upper.append(cfg['max_consecutive_days'])
    constraints=LinearConstraint(csr_matrix(np.vstack(matrices)),np.array(lower),np.array(upper))
    result=milp(patterns.cost_units.to_numpy(),integrality=np.ones(len(patterns)),bounds=Bounds(0,1),constraints=constraints,options={'time_limit':cfg['solver_time_limit_seconds'],'mip_rel_gap':cfg['solver_relative_gap']})
    if result.x is None or result.status not in [0,1]:raise ValueError(f'No hay solución factible: {result.message}')
    if np.max(np.abs(result.x-np.round(result.x)))>1e-5:raise ValueError('El solver no entregó variables binarias')
    plan=patterns.loc[result.x>.5].reset_index(drop=True);audit=audit_plan(plan,demand,employees,cfg)
    if not audit.get('cobertura_completa',False):raise ValueError(f'Solución no supera auditoría independiente: {audit}')
    return plan,{'solver_status':int(result.status),'solver_message':str(result.message),'gap_relativo':float(result.mip_gap),'cota_inferior_coste':float(result.mip_dual_bound),'objetivo_coste':float(result.fun),'variables_binarias':len(patterns),'tolerancia_gap':cfg['solver_relative_gap'],**audit}

def train(project):
    cfg=config(project);d,e=load_frame(project,'demand'),load_frame(project,'employees');plan,result=solve(candidates(e),d,e,cfg);plan.to_csv(Path(project)/'models/optimized_plan.csv',index=False);write_json(Path(project)/'models/optimization.json',result)
    from .balance import train_balance
    result['escenario_equilibrio']=train_balance(project,result['objetivo_coste'])
    description='terminó dentro de la tolerancia configurada' if result['solver_status']==0 else 'terminó por límite con una solución factible'
    alt=result['escenario_equilibrio']
    alt_state='dentro de tolerancia' if alt['solver_status']==0 else 'por límite de tiempo, con plan factible y sin certificar optimalidad'
    return report(project,'modelado',result,f"MILP binario minimiza coste pagado sujeto a cobertura, un turno diario por empleado, disponibilidad, máximo **{cfg['max_weekly_hours']} horas semanales** y **{cfg['max_consecutive_days']} días consecutivos**. Cada turno dura 8 horas y contiene dos pausas de 30 minutos sin cobertura. El solver **{description}**; gap relativo **{result['gap_relativo']:.2%}**, coste **{result['objetivo_coste']:,.2f} unidades**. Se audita la solución fuera del solver. La certificación depende de la tolerancia y los patrones disponibles; no se afirma un óptimo exacto si el gap no es cero. El escenario de equilibrio terminó **{alt_state}**, con gap de su objetivo **{alt['gap_objetivo_equilibrio']:.2%}**.")

def evaluate(project):
    cfg=config(project);d,e=load_frame(project,'demand'),load_frame(project,'employees');plan=pd.read_csv(Path(project)/'models/optimized_plan.csv');base=pd.read_csv(Path(project)/'models/baseline_plan.csv');a=audit_plan(base,d,e,cfg);b=audit_plan(plan,d,e,cfg)
    if not b.get('cobertura_completa',False):raise ValueError('Plan optimizado no supera controles')
    coverage=coverage_matrix(plan).sum(axis=1);need=d.required_agents.to_numpy();stress=np.ceil(need*1.2);deficit=np.maximum(0,stress-coverage)
    output=d.assign(covered_agents=coverage,excess_agents=coverage-need,required_plus20pct=stress,deficit_plus20pct=deficit);output.to_csv(report_path(project,'evaluacion','cobertura_por_intervalo.csv'),index=False)
    weekly=plan.groupby('employee').agg(horas_pagadas=('paid_hours','sum'),dias_trabajados=('day','size'),coste_unidades=('cost_units','sum')).reindex(e.employee,fill_value=0).reset_index();weekly.to_csv(report_path(project,'evaluacion','horas_por_empleado.csv'),index=False)
    export=plan.copy()
    def clock(slot):return f'{cfg["open_hour"]+slot//2:02d}:{30*(slot%2):02d}'
    for key in ['start_slot','lunch_slot','break_slot']:export[key.replace('_slot','_time')]=export[key].map(clock)
    export['end_time']=(export.start_slot+16).map(clock);export.to_csv(report_path(project,'evaluacion','turnos_programados.csv'),index=False)
    solver=read_json(Path(project)/'models/optimization.json');result={'baseline':a,'optimizado':b,'gap_relativo':solver['gap_relativo'],'escenario_mas20pct_deficit_agente_intervalos':float(deficit.sum()),'escenario_mas20pct_intervalos_sin_cobertura':int(np.count_nonzero(deficit)),'ahorro_frente_baseline_factible':float(a['coste_unidades']-b['coste_unidades']) if a['cobertura_completa'] else None}
    fig,axes=plt.subplots(1,2,figsize=(11,4));im=axes[0].imshow((coverage-need).reshape(7,20),aspect='auto',cmap='Blues');axes[0].set(title='Exceso de cobertura · escenario base',xlabel='Franja',ylabel='Día');fig.colorbar(im,ax=axes[0]);axes[1].bar(weekly.employee,weekly.horas_pagadas);axes[1].axhline(cfg['max_weekly_hours'],color='red',ls='--');axes[1].tick_params(axis='x',rotation=60);axes[1].set(title='Horas pagadas por empleado',ylabel='Horas');fig.tight_layout();fig.savefig(report_path(project,'evaluacion','evaluacion.png'),dpi=130);plt.close(fig)
    from .balance import evaluate_balance
    balanced,balanced_text=evaluate_balance(project)
    result.update(balanced)
    comparison=f"Ahorro frente al baseline factible: **{result['ahorro_frente_baseline_factible']:,.2f} unidades**." if a['cobertura_completa'] else 'El baseline no cubre toda la demanda; su menor coste, si lo hubiera, no demuestra ahorro comparable.'
    return report(project,'evaluacion',result,f"El plan optimizado supera cobertura y restricciones estructurales en las **140 franjas**. {comparison} Al mantener los turnos y aumentar los requisitos un 20 % (redondeo al entero superior), **{result['escenario_mas20pct_intervalos_sin_cobertura']} franjas** quedan cortas, con **{result['escenario_mas20pct_deficit_agente_intervalos']:.0f} agente-intervalos** de déficit. El escenario de estrés no se reoptimiza ni es una garantía probabilística. Son reglas didácticas, no un calendario de una empresa, cumplimiento de legislación laboral ni SLA. No se modelan habilidades, vacaciones ni rotación entre semanas.\n\n{balanced_text}")

def run_stage(project,stage):return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
