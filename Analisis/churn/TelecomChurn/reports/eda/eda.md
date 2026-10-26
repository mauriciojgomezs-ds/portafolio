# EDA de entrenamiento

Registros: **2,132**. Churn positivo: **14.54%**. La clase positiva es minoritaria.

Se explora solo train: validación selecciona el modelo y test queda reservado. No se infiere causalidad ni representatividad de estas cifras.

## Nulos por columna

```text
                        nulos
State                       0
Account length              0
Area code                   0
International plan          0
Voice mail plan             0
Number vmail messages       0
Total day minutes           0
Total day calls             0
Total day charge            0
Total eve minutes           0
Total eve calls             0
Total eve charge            0
Total night minutes         0
Total night calls           0
Total night charge          0
Total intl minutes          0
Total intl calls            0
Total intl charge           0
Customer service calls      0
Churn                       0
```

## Atributos excluidos

Total day charge, Total eve charge, Total night charge, Total intl charge
