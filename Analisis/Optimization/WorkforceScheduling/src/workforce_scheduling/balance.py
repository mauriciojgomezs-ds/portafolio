"""Escenario alternativo: equilibrio de horas y preferencias sintéticas bajo tope de coste."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import csr_matrix
from .common import config,load_frame,write_json,read_json,report_path,sha256
import warnings

class SolverLimitWarning(UserWarning):
    """Existe un plan factible, pero no se cerró el gap solicitado."""

def setup_preferences(project):
    cfg=config(project);path=Path(project)/cfg['preferences_source']
    if not path.exists():
        origin=Path(project)/'data/raw/scenario_origin.json'
        if not origin.exists():raise ValueError('Aporta preferencias documentadas; solo se generan para el escenario sintético identificado')
        employees=pd.read_csv(Path(project)/cfg['employees_source'])
        pd.DataFrame({'employee':employees.employee,'preferred_start_slot':np.arange(len(employees))%5}).to_csv(path,index=False)
    return path

def solve_balanced(patterns,demand,employees,preferences,cfg,cost_reference):
    from .analysis import coverage_matrix,audit_plan
    if preferences.employee.duplicated().any() or set(preferences.employee)!=set(employees.employee) or not preferences.preferred_start_slot.isin(range(5)).all():raise ValueError('Preferencias requieren todos los empleados una vez y un inicio válido')
    if cost_reference<0 or cfg['balanced_extra_cost_ratio']<0 or cfg['balance_hours_weight']<=0 or cfg['preference_miss_weight']<0:raise ValueError('Parámetros del escenario no válidos')
    n=len(patterns);cover=coverage_matrix(patterns);rows=[np.column_stack([cover,np.zeros((140,2))])];lower=list(demand.required_agents);upper=[np.inf]*140
    def add(row,lo,hi):rows.append(np.asarray(row,dtype=float)[None,:]);lower.append(lo);upper.append(hi)
    for employee in employees.employee:
        own=patterns.employee.eq(employee).to_numpy();hours=own*patterns.paid_hours.to_numpy()
        for day in range(7):add(np.r_[own&patterns.day.eq(day),0,0],0,1)
        add(np.r_[hours,0,0],0,cfg['max_weekly_hours'])
        window=cfg['max_consecutive_days']+1
        for start in range(8-window):add(np.r_[own&patterns.day.between(start,start+window-1),0,0],0,cfg['max_consecutive_days'])
        # Variables extra: mínimo de horas y máximo de horas entre toda la plantilla.
        add(np.r_[hours,-1,0],0,np.inf);add(np.r_[hours,0,-1],-np.inf,0)
    cap=cost_reference*(1+cfg['balanced_extra_cost_ratio']);add(np.r_[patterns.cost_units,0,0],0,cap)
    desired=preferences.set_index('employee').preferred_start_slot;miss=patterns.start_slot.ne(patterns.employee.map(desired)).astype(float).to_numpy()
    objective=np.r_[cfg['preference_miss_weight']*miss,-cfg['balance_hours_weight'],cfg['balance_hours_weight']]
    result=milp(objective,integrality=np.r_[np.ones(n),0,0],bounds=Bounds(np.zeros(n+2),np.r_[np.ones(n),cfg['max_weekly_hours'],cfg['max_weekly_hours']]),constraints=LinearConstraint(csr_matrix(np.vstack(rows)),np.array(lower),np.array(upper)),options={'time_limit':cfg['solver_time_limit_seconds'],'mip_rel_gap':cfg['solver_relative_gap']})
    if result.x is None or result.status not in [0,1] or np.max(np.abs(result.x[:n]-np.round(result.x[:n])))>1e-5:raise ValueError(f'Escenario sin solución binaria factible: {result.message}')
    plan=patterns.loc[result.x[:n]>.5].reset_index(drop=True);audit=audit_plan(plan,demand,employees,cfg)
    if not audit.get('cobertura_completa') or audit['coste_unidades']>cap+1e-6:raise ValueError('Escenario no supera auditoría o tope de coste')
    hours=plan.groupby('employee').paid_hours.sum().reindex(employees.employee,fill_value=0);mismatches=int(plan.start_slot.ne(plan.employee.map(desired)).sum());actual=cfg['balance_hours_weight']*float(hours.max()-hours.min())+cfg['preference_miss_weight']*mismatches
    if not np.isclose(actual,result.fun,atol=1e-5):raise ValueError('Objetivo declarado no coincide con horas y preferencias auditadas')
    return plan,{'solver_status':int(result.status),'solver_message':str(result.message),'gap_objetivo_equilibrio':float(result.mip_gap),'objetivo_puntuacion':actual,'tope_coste_unidades':cap,'coste_referencia_unidades':cost_reference,'rango_horas':float(hours.max()-hours.min()),'preferencias_incumplidas':mismatches,**audit}

def train_balance(project,reference):
    from .analysis import candidates
    cfg=config(project);d,e=load_frame(project,'demand'),load_frame(project,'employees');path=setup_preferences(project);prefs=pd.read_csv(path)
    plan,info=solve_balanced(candidates(e),d,e,prefs,cfg,reference)
    if info['solver_status']==1:
        warnings.warn(f"El solver del escenario de equilibrio alcanzó su límite de tiempo. Plan factible auditado; gap del objetivo alternativo {info['gap_objetivo_equilibrio']:.2%}, sin certificar optimalidad.",SolverLimitWarning)
    plan.to_csv(Path(project)/'models/balanced_plan.csv',index=False);info['preferencias_sha256']=sha256(path);write_json(Path(project)/'models/balance.json',info)
    return info

def evaluate_balance(project):
    from .analysis import audit_plan
    cfg=config(project);d,e=load_frame(project,'demand'),load_frame(project,'employees');prefs=pd.read_csv(Path(project)/cfg['preferences_source']).set_index('employee').preferred_start_slot
    records=[];hours=[]
    for name,file in [('coste_minimo','optimized_plan.csv'),('equilibrio_preferencias','balanced_plan.csv')]:
        plan=pd.read_csv(Path(project)/'models'/file);audit=audit_plan(plan,d,e,cfg)
        if not audit.get('cobertura_completa'):raise ValueError('Plan comparado no factible')
        totals=plan.groupby('employee').paid_hours.sum().reindex(e.employee,fill_value=0);miss=int(plan.start_slot.ne(plan.employee.map(prefs)).sum())
        records.append({'escenario':name,'coste_unidades':audit['coste_unidades'],'horas_pagadas':float(totals.sum()),'rango_horas':float(totals.max()-totals.min()),'desviacion_horas':float(totals.std(ddof=0)),'preferencias_incumplidas':miss,'cobertura_completa':True})
        hours.append(pd.DataFrame({'employee':e.employee,'horas_pagadas':totals.to_numpy(),'escenario':name}))
    compare=pd.DataFrame(records);compare.to_csv(report_path(project,'evaluacion','comparacion_equilibrio.csv'),index=False);pd.concat(hours).to_csv(report_path(project,'evaluacion','horas_comparadas.csv'),index=False)
    import matplotlib.pyplot as plt
    pivot=pd.concat(hours).pivot(index='employee',columns='escenario',values='horas_pagadas');ax=pivot.plot.bar(figsize=(10,4));ax.set(ylabel='Horas pagadas',title='Escenarios factibles · plantilla sintética');ax.figure.tight_layout();ax.figure.savefig(report_path(project,'evaluacion','equilibrio.png'),dpi=130);plt.close(ax.figure)
    extra=records[1]['coste_unidades']/records[0]['coste_unidades']-1
    solver=read_json(Path(project)/'models/balance.json')
    info={'escenarios_equilibrio':records,'incremento_coste_relativo':float(extra),'tope_incremento_relativo':cfg['balanced_extra_cost_ratio'],'equilibrio_solver_status':solver['solver_status'],'equilibrio_gap_objetivo':solver['gap_objetivo_equilibrio']}
    write_json(report_path(project,'evaluacion','equilibrio.json'),info)
    text=f"## Equilibrio y preferencias\n\nAmbos planes cubren la demanda. El escenario alternativo reduce o intercambia rango de horas y preferencias bajo un tope de coste: rango **{records[0]['rango_horas']:.0f} → {records[1]['rango_horas']:.0f} horas**, preferencias incumplidas **{records[0]['preferencias_incumplidas']} → {records[1]['preferencias_incumplidas']}**, coste **{records[1]['coste_unidades']:,.2f} unidades** (**{extra:+.2%}** respecto al plan de coste mínimo). La función objetivo pondera rango de horas y turnos fuera del inicio preferido; su gap corresponde a esa puntuación, no a minimizar coste. Preferencias y reglas son sintéticas; equilibrar horas es una medida específica y no certifica equidad laboral.\n"
    termination='terminó dentro de la tolerancia configurada' if solver['solver_status']==0 else 'alcanzó el límite de tiempo con una solución factible; no se certifica optimalidad'
    text+=f"\nEl solver alternativo **{termination}**; gap de su objetivo **{solver['gap_objetivo_equilibrio']:.2%}**.\n"
    report_path(project,'evaluacion','equilibrio.md').write_text(text,encoding='utf-8')
    return info,text
