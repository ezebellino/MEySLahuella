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

## Requisitos adicionales

Antes de ejecutar la nueva version, instala CustomTkinter:

```bash
pip install customtkinter
```

## Version web (React + API) - Gestion centralizada de hosts

Se agrego una nueva arquitectura para operar desde un host central y administrar otros hosts por red.

### Backend API (Python)

Archivo principal: `api_server.py`

Funciones incluidas:
- operacion local existente (antena, mover `.dat`, estado de tags)
- gestion de hosts remotos con credenciales SSH
- descubrimiento de hosts en subred (`10.95.25.0/24`)
- operaciones remotas:
  - ver archivos y directorios
  - reiniciar terminal o servicio remoto
  - ejecutar comandos remotos
  - transmitir datos texto al servidor remoto

### Frontend React

Carpeta: `frontend/`

Incluye:
- dashboard modernizado
- panel de hosts con alta, edicion y baja
- escaneo de subred
- explorador remoto de archivos
- operaciones de terminal y transferencia

### Instalacion y ejecucion

1. Instalar dependencias API:

```bash
pip install -r requirements-api.txt
```

2. Levantar API:

```bash
python run_api.py
```

3. Levantar frontend:

```bash
cd frontend
npm install
npm run dev
```

### Inicio y parada silenciosa

Desde la carpeta del proyecto:
- doble click en `start_app_silent.vbs` para iniciar en segundo plano
- doble click en `stop_app_silent.vbs` para detener

Alternativa por comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_app_background.ps1
powershell -ExecutionPolicy Bypass -File .\stop_app_background.ps1
```

Estado de procesos:

```powershell
powershell -ExecutionPolicy Bypass -File .\app_process_status.ps1
```

Los PID se guardan en `.run\lahuella-api.pid` y `.run\lahuella-web.pid`.

### Hosts objetivo recomendados

- DNS: `srvlahuella.lahuella.local`
- IP: `192.168.2.10`
- subred actualizada: `10.95.25.0/24`

### Persistencia de hosts

- archivo runtime: `data/hosts.json` (ignorado en git)
- ejemplo de estructura: `data/hosts.example.json`
- credenciales:
  - se almacenan cifradas en reposo (`password_enc`)
  - en Windows se usa DPAPI automaticamente
  - incluyen rotacion con verificacion y rollback automatico

### Scripts utiles para pruebas en red

1. Diagnostico completo de red y puertos:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\collect_network_diagnostics.ps1
```

2. Test rapido de credenciales Windows/SMB:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test_windows_credentials.ps1 -Server 10.95.25.10 -Username "LAHUELLA\Via" -Password "TU_PASSWORD"
```

3. Precarga automatica de vias en la API local:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\preload_vias.ps1 -Range 10 -Password "TU_PASSWORD"
```

### Nota de protocolo remoto

La configuracion soporta tipo de host `windows` en el panel/API:
- descubrimiento recomendado por puerto `445` (SMB)
- operaciones de archivos por SMB
- operaciones de comando o reinicio por WinRM (`5985`) cuando esta habilitado
- chequeo de credenciales desde el panel para validar usuario y password por host

### Modo portable para pendrive

1. Construir bundle portable:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_portable_bundle.ps1
```

2. Copiar `portable\SistemasLaHuellaPortable` al pendrive.
3. En la PC destino ejecutar:
- `start_portable_silent.vbs`
- abrir `http://127.0.0.1:5173`
- `stop_portable_silent.vbs` para cierre

Mas detalle en `PORTABLE_PENDRIVE.md`.

### Modo portable total

Genera un paquete autonomo con ejecutables propios para API y frontend, sin requerir Python ni Node en la PC destino:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_portable_total_bundle.ps1
```

Salida:

`portable\SistemasLaHuellaPortableTotal`
