"""Etapas locales de Anomalías en temperatura de una máquina."""
from .data import prepare
from .explore import explore
from . import temporal as analysis

def run_stage(project,stage):
    actions={'preparacion':prepare,'eda':explore,'baseline':analysis.baseline,'modelado':analysis.train,'evaluacion':analysis.evaluate}
    return actions[stage](project)
