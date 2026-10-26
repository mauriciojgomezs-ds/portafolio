"""Etapas locales de Pronóstico semanal de compras."""
from .data import prepare
from .explore import explore
from . import temporal as analysis

def run_stage(project,stage):
    actions={'preparacion':prepare,'eda':explore,'baseline':analysis.baseline,'modelado':analysis.train,'evaluacion':analysis.evaluate}
    return actions[stage](project)
