"""Etapas locales de Categorías de películas desde su sinopsis."""
from .data import prepare
from .explore import explore
from . import text as analysis

def run_stage(project,stage):
    actions={'preparacion':prepare,'eda':explore,'baseline':analysis.baseline,'modelado':analysis.train,'evaluacion':analysis.evaluate}
    return actions[stage](project)
