"""Etapas locales de Recomendación colaborativa de películas."""
from .data import prepare
from .explore import explore
from . import collaborative as analysis

def run_stage(project,stage):
    actions={'preparacion':prepare,'eda':explore,'baseline':analysis.baseline,'modelado':analysis.train,'evaluacion':analysis.evaluate}
    return actions[stage](project)
