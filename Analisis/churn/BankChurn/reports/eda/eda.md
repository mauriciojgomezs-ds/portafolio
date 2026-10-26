# EDA de entrenamiento

Registros: **6,000**. Churn positivo: **20.38%**. La clase positiva es minoritaria.

Se explora solo train: validación selecciona el modelo y test queda reservado. No se infiere causalidad ni representatividad de estas cifras.

## Nulos por columna

```text
                 nulos
RowNumber            0
CustomerId           0
Surname              0
CreditScore          0
Geography            0
Gender               0
Age                  0
Tenure               0
Balance              0
NumOfProducts        0
HasCrCard            0
IsActiveMember       0
EstimatedSalary      0
Exited               0
```

## Atributos excluidos

RowNumber, CustomerId, Surname
