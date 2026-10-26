"""Ejecuta 01–05 desde cualquier directorio con el Python activo."""
import argparse
from pathlib import Path
import sys
PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/'src'))
from telecom_churn.ejecucion import ejecutar_secuencia

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout',type=int,default=900,help='Límite de segundos por celda')
    args=parser.parse_args()
    raise SystemExit(ejecutar_secuencia(PROJECT_ROOT,timeout=args.timeout))
