"""Prepara la fuente independiente sin reemplazar una copia existente."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from retail_kpi_analysis.analysis import setup
print(setup(root))
