# Ejecutar ActivityChurn

Este proyecto se puede copiar a una carpeta distinta con cualquier nombre, conservando sus archivos locales. No depende de una carpeta temática, de otro proyecto ni de funciones globales del portafolio.

## Preparación

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyterlab
```

Verifica las entradas en [fuentes.md](fuentes.md), selecciona ese entorno en Jupyter o VS Code y ejecuta 00. Si instala librerías, reinicia el kernel y repite. Guarda y cierra 01–05 y ejecuta las tres celdas de 06 para recorrerlas secuencialmente. También puedes usar `python scripts/execute_notebooks.py` o ejecutar los notebooks individuales en orden.

## Responsabilidades de las carpetas

`src/activity_churn` contiene funciones importables. `scripts` contiene comandos; `tests` verifica reglas del proyecto. `data/raw` contiene sus fuentes; los demás datos, modelos y reportes se producen localmente. `pyproject.toml` declara el paquete y `requirements.txt` instala ese paquete con sus dependencias de notebooks.

El maestro utiliza un kernel independiente por etapa con el mismo Python activo, se detiene ante errores y conserva una copia parcial en `reports/runs/fallos`. Los reportes tienen nombres estables y pueden corresponder a etapas de pasadas distintas si una secuencia falla: revisa siempre `reports/ejecucion/resumen.json`.

## Revisión

Consulta `reports/alertas` para avisos agrupados, su significado y acciones sugeridas. La ausencia de avisos no valida el modelo. Las cifras y conclusiones se recalculan al ejecutar. La [metodología](metodologia.md) explica qué se mide y las limitaciones.

Para comprobar los tests: `python -m unittest discover -s tests -v`.
