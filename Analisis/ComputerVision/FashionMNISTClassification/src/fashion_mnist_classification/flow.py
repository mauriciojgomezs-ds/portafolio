"""Puntos de entrada de las cinco etapas del proyecto."""
from .data import prepare
from .vision import explore, baseline, train, evaluate

def run_stage(project, stage):
    return {'preparacion':prepare,'eda':explore,'baseline':baseline,'modelado':train,'evaluacion':evaluate}[stage](project)
