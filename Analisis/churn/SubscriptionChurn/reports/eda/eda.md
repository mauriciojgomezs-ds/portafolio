# EDA de entrenamiento

Registros: **352,665**. Churn positivo: **56.71%**. La clase negativa es minoritaria.

Se explora solo train: validación selecciona el modelo y test queda reservado. No se infiere causalidad ni representatividad de estas cifras.

## Nulos por columna

```text
                   nulos
CustomerID             0
Age                    0
Gender                 0
Tenure                 0
Usage Frequency        0
Support Calls          0
Payment Delay          0
Subscription Type      0
Contract Length        0
Total Spend            0
Last Interaction       0
Churn                  0
```

## Atributos excluidos

CustomerID
