"""Regenera el informe con resultados locales existentes; no ejecuta modelos."""
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / 'src'))
from email_community_analysis.informe import generar_informe
if __name__ == '__main__':
    print(generar_informe(PROJECT_ROOT))
