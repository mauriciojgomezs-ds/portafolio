# Estructura de SmartFood

## Organización de reportes

Los reportes se agrupan por etapa dentro de `reports/` y se generan con nombres estables. Repetir una etapa reemplaza sus archivos vigentes.

| Carpeta | Archivos vigentes |
| --- | --- |
| `alertas/` | `01_preparacion_datos.json`, `02_analisis_exploratorio.json`, `03_baseline_perfil_usuario.json`, `04_filtrado_colaborativo_nmf.json`, `05_clasificacion_ranking_svm.json` |
| `eda/` | `metricas_eda.json`, `conclusiones_eda.md` e inspecciones y figuras en `recipes/`, `reviews/`, `recipes_filtrado/` y `reviews_filtrado/` |
| `ejecucion/` | `resumen.json` |
| `entorno/` | `environment.json` y `environment.requirements.txt` |

Las copias parciales de fallos se conservan en `runs/fallos/`. Revisa `ejecucion/resumen.json` para distinguir una secuencia completa de ejecuciones parciales. Cada proyecto crea sus carpetas localmente y conserva su independencia.

Las inspecciones de cada dataset se encuentran en `eda/<dataset>/`. Los notebooks 03–05 guardan sus modelos y recomendaciones en `models/` y `data/output/`, y exportan cifras y conclusiones en `reports/baseline/`, `reports/modelado/` y `reports/evaluacion/`. El informe integral reúne esos reportes.

## Informe integral

Consulta el [informe integral](../reports/informe_final/informe_final.md). Se actualiza con 06 y reúne cifras, conclusiones, limitaciones y próximos pasos. Para regenerarlo con resultados existentes usa `python scripts/generate_report.py`. Consulta la [guía del informe](informe_final.md).
