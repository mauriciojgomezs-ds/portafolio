# Configuración del entorno

El punto de entrada del proyecto es [00_configuracion_entorno.ipynb](../notebooks/00_configuracion_entorno.ipynb). Se ejecuta antes de preparar datos o entrenar modelos.

## Archivos de dependencias

| Archivo | Función |
| --- | --- |
| [requirements.txt](../requirements.txt) | Instalar dependencias directas para el proyecto y los notebooks, además del paquete local mediante `-e .` |
| [pyproject.toml](../pyproject.toml) | Declarar el paquete Python, sus dependencias y el extra `notebooks` |
| `reports/entorno/environment.requirements.txt` | Registrar versiones exactas de la comprobación vigente, incluidas dependencias transitivas |
| [requirements_ejecucion.txt](requirements_ejecucion.txt) | Registro del entorno instalado en la primera sesión de ejecución; conserva una incidencia de carga de scikit-learn |

Los rangos de `requirements.txt` y `pyproject.toml` deben mantenerse alineados cuando se añada o cambie una dependencia. Los archivos con versiones exactas registran un entorno observado; no certifican por sí solos que el proyecto funcione en otro equipo.

## Iniciar Jupyter

Desde la carpeta SmartFood, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install jupyterlab ipykernel packaging
.\.venv\Scripts\python.exe -m ipykernel install --user --name smartfood --display-name "Python (SmartFood)"
.\.venv\Scripts\python.exe -m jupyterlab
```

La instalación inicial permite abrir el notebook 00. Al ejecutarlo, instala las dependencias del proyecto que todavía falten. También puedes instalar todo previamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Ejecuta ese comando desde SmartFood porque el archivo incluye una referencia editable a la carpeta actual. El notebook establece esa carpeta automáticamente antes de llamar al instalador.

## Qué comprueba el notebook 00

1. Identifica la raíz del proyecto, muestra `sys.executable` y comprueba Python 3.10 o posterior.
2. Compara las versiones instaladas con los rangos de `requirements.txt` y comprueba que el paquete local esté instalado desde esta carpeta.
3. Instala con el Python del kernel si falta algún requisito o el paquete local. No solicita actualizaciones de paquetes que ya cumplen los rangos.
4. Ejecuta `pip check` y comprueba imports en procesos separados, incluidos métricas, NMF y SVM de scikit-learn. Cada import tiene un límite de 60 segundos.
5. Guarda `reports/entorno/environment.json` y `environment.requirements.txt`, reemplazando la versión anterior y conservando la fecha dentro del JSON. Muestra la disponibilidad de los archivos de entrada por separado.

Seleccionar un kernel diferente puede instalar las bibliotecas en otro Python. Si hubo una instalación, reinicia el kernel y repite 00 antes de seguir. Los procesos de diagnóstico comprueban el entorno instalado, pero no reemplazan el reinicio del kernel activo.

## Interpretar el diagnóstico

- **OK:** la versión cumple o el import pasó, según la comprobación.
- **ERROR:** el proceso de importación devolvió un error; el informe conserva su detalle.
- **TIMEOUT:** el import no terminó en el plazo. No demuestra que la biblioteca esté ausente; requiere revisar la causa.
- **Entorno listo:** versiones, imports y `pip check` pasaron. Las comprobaciones no incluyen entrenamiento ni validación de resultados.

Un paquete puede estar instalado y no poder cargar sus componentes nativos. En comprobaciones anteriores se observó un bloqueo de Control de aplicaciones de Windows para una DLL de scikit-learn. El informe más reciente, generado el 6 de octubre de 2026 a las 19:27 en America/Santiago, pasa todos los imports en otro intérprete, Python 3.14. Ese resultado no demuestra que el bloqueo se haya resuelto en `.venv`. El notebook lo registra; no cambia políticas del sistema ni lo soluciona reinstalando automáticamente una biblioteca que cumple su versión.

La ausencia de CSV o Parquet no impide comprobar las bibliotecas. Sí impide ejecutar la preparación de datos. Los resultados de ejecución del proyecto se documentan en el [registro de ejecuciones](ejecuciones.md).

Después de la limpieza de reportes y de la ejecución del maestro, los informes de 00 todavía no se regeneraron. El resultado satisfactorio de imports citado arriba es anterior y está en el respaldo local. La nueva pasada de 01–05 utilizó Python 3.14.4, pero falta guardar su comprobación de entorno y versiones exactas ejecutando 00. El maestro no incluye esa etapa.
