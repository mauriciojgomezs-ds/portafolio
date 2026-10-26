"""Prepara la fuente independiente sin reemplazar una copia existente."""
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from industrial_anomaly_detection.analysis import setup
print(setup(root))
