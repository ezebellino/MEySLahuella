# MEyS La Huella

Aplicacion de escritorio para operacion de vias, desarrollada en Python con `CustomTkinter`.

La herramienta concentra tareas operativas frecuentes en una sola interfaz:
- consulta de informacion del puesto
- deteccion de puertos COM
- apertura de herramientas auxiliares
- lectura y actualizacion de configuracion de antena
- control de archivos de tags
- movimiento de archivos `.dat`
- apertura automatica del configurador de antena segun la via detectada

## Estado actual

La aplicacion hoy cuenta con:
- login integrado dentro de la misma ventana
- dashboard con navegacion lateral
- mensajes de estado y notificaciones dentro de la UI
- persistencia local de preferencias
- configuracion centralizada
- ejecutable empaquetado con PyInstaller

## Requisitos

- Windows 10 o superior
- Python 3.12 si se ejecuta desde codigo fuente
- Las herramientas externas y archivos operativos deben existir en las rutas configuradas

## Ejecucion desde codigo

Desde la raiz del proyecto:

```powershell
.\env\Scripts\python.exe .\src\ui\Interfaz.py
```

Tambien puede ejecutarse con:

```powershell
.\env\Scripts\python.exe .\main.py
```

## Ejecutable generado

El ejecutable empaquetado actual se encuentra en:

`dist\MEySLahuella.exe`

Ruta completa de ejemplo:

`C:\Users\ezebe\OneDrive\Proyectos\Peaje\dist\MEySLahuella.exe`

## Credenciales por defecto

- Usuario: `admin`
- Contrasena: `1234`

Estas credenciales hoy se leen desde la configuracion local.

## Configuracion local

La app guarda y lee configuracion desde:

`%USERPROFILE%\.meys_lahuella\settings.json`

Ese archivo centraliza:
- ultimo usuario utilizado
- ultima vista abierta
- ruta de origen para archivos `.dat`
- ruta de destino
- ruta del ejecutable de testeo
- rutas de configuradores de antena
- ubicacion de `TciNumero.ini`
- archivos de tags
- grupos de vias para cada configurador
- credenciales de acceso

## Configuracion por defecto

Valores importantes incluidos en `src/config/settings.py`:

- `source_path`: `C:\Via\Aplicacion`
- `testeo_path`: `C:\Via\Testeo\Testeo.exe`
- `reader_test_path`: `C:\APPS\ReaderTest.exe`
- `uip_reader_path`: `C:\Teste Antena\UipReader01demomain.exe`
- `antenna_ini_dir`: `C:\Windows\`
- `antenna_ini_name`: `TciNumero.ini`

Asignacion de configuradores de antena:
- `ReaderTest.exe`: vias `51`, `52`, `53`, `9`, `10`, `11`
- `UipReader01demomain.exe`: vias `54`, `55`, `7`, `8`

## Funcionalidades principales

### 1. Panel operativo

- muestra nombre de equipo, IP local y via detectada
- lista puertos COM disponibles
- permite abrir la herramienta de testeo
- muestra mensajes de estado y notificaciones operativas

### 2. Panel de archivos y antena

- consulta estado de archivos de tags
- lee IP de antena y potencia actual
- permite actualizar potencia con validacion
- abre el configurador de antena correcto segun la via
- mueve archivos `.dat` a una carpeta de destino con subcarpeta fechada

## Comportamiento de archivos `.dat`

Cuando se ejecuta el movimiento:
- se buscan archivos `.dat` de forma recursiva en la carpeta de origen
- se crea una subcarpeta con fecha en la carpeta de destino
- si esa carpeta ya existe, se agrega un sufijo numerico

Ejemplos:
- `22.03.26`
- `22.03.26-1`
- `22.03.26-2`

## Tests

Hay tests basicos para servicios en:
- `tests/test_antena_services.py`
- `tests/test_mover_services.py`

Ejecutarlos:

```powershell
py -3 -m unittest discover -s tests -v
```

## Empaquetado

El proyecto usa PyInstaller con:

- spec: `application/Interfaz.spec`
- icono: `application/icon.ico`

Generar ejecutable:

```powershell
.\env\Scripts\pyinstaller.exe .\application\Interfaz.spec --clean
```

## Estructura principal

- `src/ui/Interfaz.py`: dashboard principal
- `src/ui/login.py`: login embebido
- `src/ui/theme_utils.py`: carga de tema
- `src/config/settings.py`: configuracion por defecto y persistencia
- `src/app/antena_services.py`: lectura y escritura de configuracion de antena
- `src/app/tag_services.py`: consulta de archivos de tags
- `src/app/mover_services.py`: movimiento de archivos `.dat`

## Recomendaciones de distribucion interna

- distribuir el `.exe` desde `dist\MEySLahuella.exe`
- validar en cada puesto las rutas externas antes de uso
- revisar `settings.json` local si cambia alguna ruta o credencial
- mantener `build/` fuera del versionado porque es salida temporal de PyInstaller

## Pendientes recomendados

- pantalla administrativa para editar configuracion sin tocar JSON
- autenticacion real con usuarios por rol
- versionado de releases
- mejoras de logging y soporte operativo
