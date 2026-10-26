# Regresión de potencia eléctrica: modelado

Se elige **HGB_hojas_31** por MAE de validación, entre Ridge y boosting. El modelo se ajusta exclusivamente en train y no se reentrena con validación. Una partición de calibración separada de **953 casos** fija un radio conformal de **±4.942 MW**, con cobertura nominal **90%**. Test permanece reservado. La cobertura marginal requiere intercambiabilidad; no garantiza cobertura condicional ni temporal.
