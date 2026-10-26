# Registro de ejecución

00 y 06 se verificaron el 7 de octubre de 2026. El maestro completó 01–05: inicio UTC 2026-10-07T15:52:33.127550+00:00; fin UTC 2026-10-07T15:53:01.757263+00:00. Los siete notebooks tienen tres celdas de código ejecutadas sin salidas de error.

La MLP obtuvo accuracy 85.18 % frente a 81.01 % del baseline. Las cifras y conclusiones vigentes están en el [informe integral](../reports/informe_final/informe_final.md).

Los dos candidatos de MLP alcanzaron el máximo de 40 iteraciones sin converger; los avisos están en [alertas de modelado](../reports/alertas/04_modelado.json). Se conserva el protocolo inicial: no se ajustaron iteraciones ni alpha después de observar test. Revisar convergencia es una ampliación pendiente, con selección en validación.

Se aprobaron seis pruebas y los enlaces locales. Una copia renombrada fuera de la carpeta temática pasó generador, pruebas y bootstrap desde notebooks; esta comprobación no incluyó reentrenar ni copiar datos/modelos. Consulta el [registro](verificacion.json).
