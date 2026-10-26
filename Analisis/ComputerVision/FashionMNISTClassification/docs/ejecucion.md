# Ejecutar este proyecto

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Selecciona ese entorno en VS Code o Jupyter y ejecuta 00. Si instala dependencias, reinicia el kernel y repite. 00 descarga las fuentes solo si faltan y comprueba integridad; después el entrenamiento funciona con archivos locales. Ejecuta 06 para recorrer 01–05. Los notebooks individuales y el maestro tienen tres celdas de código.

Alternativa: `python scripts/download_sources.py` y `python scripts/execute_notebooks.py`. Para regenerar el informe sin entrenar: `python scripts/generate_report.py`. Para comprobar el código: `python -m unittest discover -s tests -v`.

El maestro usa kernels independientes, se detiene ante un fallo y guarda `reports/ejecucion/resumen.json` y copias parciales en `reports/runs/fallos/`. Los reportes se reemplazan con nombres estables. Revisa alertas y fechas antes de publicar; una ausencia de warnings no acredita calidad.
