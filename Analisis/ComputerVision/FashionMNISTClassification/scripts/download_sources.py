"""Descarga oficial con comprobación de integridad, sin reemplazar entradas existentes."""
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT/'src'))
from fashion_mnist_classification.data import download
if __name__ == '__main__':
    print(download(PROJECT_ROOT))
