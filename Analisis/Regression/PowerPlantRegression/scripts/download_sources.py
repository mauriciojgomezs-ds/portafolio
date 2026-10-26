from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from power_plant_regression.analysis import setup
print(setup(root))
