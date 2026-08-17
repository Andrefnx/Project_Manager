# Organizador-Respaldos-Windows

Automatización en Python para organizar y respaldar archivos en Windows según reglas de fecha, tipo y nombre. En la configuración actual está orientada a una jornada nocturna: revisa una carpeta de trabajo a las 07:00 y, si han pasado al menos 2 horas sin actividad, mueve los archivos `.indd` elegibles a `respaldo/<mes>/<día>`.

## Cómo funciona

![Flujo de archivos en Windows](docs/windows-file-flow.svg)

Para un cierre del **17-08-2026**, la ventana de trabajo comienza el 16 a las 19:00 y termina el 17 a las 06:59. Si la última modificación fue a las 04:00, al ejecutarse a las 07:00 ya se cumple la regla de inactividad.

La configuración actual procesa `.indd` del nivel principal de `SOURCE_FOLDER`. `BACKUP_FOLDER` se excluye para evitar que el propio respaldo cuente como actividad.

## Arquitectura

- `src/main.py`: punto de entrada, argumentos, logging y códigos de salida.
- `src/config.py`: carga `SOURCE_FOLDER`, `BACKUP_FOLDER` y `LOG_LEVEL` desde `.env`.
- `src/file_mover.py`: calcula la jornada, comprueba la inactividad, filtra archivos, construye el destino y realiza los movimientos.
- `scripts/setup_task.ps1`: registra la ejecución diaria en el Programador de tareas de Windows.
- `tests/`: pruebas automatizadas con carpetas temporales.

## Instalación

Requiere Python 3.11 o superior.

```powershell
git clone https://github.com/Andrefnx/Project_Manager.git
cd Project_Manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Configuración

Las rutas locales se mantienen fuera del código mediante `.env`:

```env
SOURCE_FOLDER=C:\Ruta\De\Trabajo\Paginas diario
BACKUP_FOLDER=C:\Ruta\De\Trabajo\Paginas diario\respaldo
LOG_LEVEL=INFO
```

`.env` está incluido en `.gitignore` y no debe publicarse.

## Ejecución manual

```powershell
python src/main.py
```

El proceso valida el origen, crea el respaldo cuando hace falta, comprueba la última actividad y procesa cada archivo de forma independiente. Si un nombre ya existe en el destino, utiliza un sufijo como `pagina (1).indd` en lugar de sobrescribirlo.

### Dry-run

```powershell
python src/main.py --dry-run
```

Realiza todas las comprobaciones y registra qué movimientos corresponderían sin modificar los archivos.

### Probar otra fecha de cierre

```powershell
python src/main.py --date 17-08-2026 --dry-run
```

`--date` permite reproducir el cálculo de una jornada determinada sin cambiar la fecha del equipo.

## Programador de tareas de Windows

`scripts/setup_task.ps1` registra una tarea diaria a las **07:00** usando rutas absolutas y el usuario actual.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_task.ps1
```

Comprobarla:

```powershell
Get-ScheduledTask -TaskName "Organizador-Respaldos-Windows"
Get-ScheduledTaskInfo -TaskName "Organizador-Respaldos-Windows"
```

Ejecutarla manualmente:

```powershell
Start-ScheduledTask -TaskName "Organizador-Respaldos-Windows"
```

Eliminarla:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_task.ps1 -Remove
```

La ejecución a las 07:00 exige que hayan transcurrido **al menos 120 minutos sin actividad**. No presupone que el movimiento ocurra exactamente dos horas después del último cambio.

## Reglas de movimiento

- `work_window_for()`: calcula el inicio y fin de la jornada.
- `latest_source_activity()`: obtiene la modificación más reciente del origen excluyendo el respaldo.
- `source_is_idle()`: comprueba el periodo mínimo sin actividad.
- `candidate_indesign_files()`: selecciona los `.indd` pertenecientes a la jornada.
- `dated_destination()`: genera la estructura `mes/día`.
- `safe_destination()`: evita sobrescrituras mediante sufijos numéricos.
- `process_backup()`: coordina el proceso y continúa si un elemento falla.

## Pruebas

```powershell
pytest -q
```

Las pruebas utilizan directorios temporales y cubren el filtro `.indd`, la ventana nocturna, las 2 horas de inactividad, `--dry-run`, origen inexistente y nombres de destino seguros.

## Códigos de salida

- `0`: ejecución completada sin errores.
- `1`: uno o más elementos fallaron, pero el resto continuó.
- `2`: configuración inválida o carpeta de origen inexistente.
- `3`: error fatal inesperado.

## Solución de errores

**No se mueve ningún `.indd`:** comprueba que la modificación pertenezca a la ventana de la jornada y que hayan transcurrido al menos 2 horas sin actividad.

**La tarea usa otro Python:** vuelve a registrarla indicando el ejecutable del entorno virtual:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_task.ps1 -PythonExe ".\.venv\Scripts\python.exe"
```

**Ya existe un archivo con el mismo nombre:** no se sobrescribe; se genera automáticamente un nombre con sufijo numérico.

## Estructura

```text
src/
  main.py
  config.py
  file_mover.py
tests/
scripts/
  setup_task.ps1
docs/
  windows-file-flow.svg
.env.example
requirements.txt
README.md
LICENSE
```

## Licencia

MIT.
