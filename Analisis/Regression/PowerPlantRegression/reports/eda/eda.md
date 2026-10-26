# Regresión de potencia eléctrica: eda

Train contiene **5716 observaciones**. Correlación temperatura–potencia **-0.948**, asociación **fuerte** bajo la regla declarada. Esta clasificación se actualiza con los datos y no implica causalidad. Multicolinealidad entre AT, V, AP y RH: VIF máximo **6.07** en **AT**, nivel **moderada** (umbral descriptivo VIF>=10 alta, >=5 moderada). Un VIF alto afecta la interpretación de coeficientes en Ridge, no la capacidad predictiva del modelo elegido por MAE. El dataset corresponde a operación a plena carga; no acredita desempeño en otros regímenes.
