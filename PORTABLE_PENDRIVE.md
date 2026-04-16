# Modo Portable para Pendrive

Este modo permite ejecutar el sistema en una PC de estacion sin levantar `npm run dev`.

## 1) Preparar paquete portable (en tu PC de desarrollo)

Desde la raiz del proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_portable_bundle.ps1
```

Se genera:

`portable\SistemasLaHuellaPortable`

Copiar esa carpeta completa al pendrive.

## 1.b) Preparar paquete portable total

Este modo genera un bundle autonomo que no requiere `Python` ni `Node` en la PC destino.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_portable_total_bundle.ps1
```

Se genera:

`portable\SistemasLaHuellaPortableTotal`

## 2) Ejecutar en la PC de la estacion

Dentro de `SistemasLaHuellaPortable`:

- Doble click en `start_portable_silent.vbs` (sin ventanas de terminal).
- Abrir: `http://127.0.0.1:5173`
- Si queres un acceso directo en el escritorio con icono:

```powershell
powershell -ExecutionPolicy Bypass -File .\create_desktop_shortcut.ps1 -Mode portable
```

- Si queres tambien el acceso directo para cerrar:

```powershell
powershell -ExecutionPolicy Bypass -File .\create_desktop_shortcut.ps1 -Mode portable -Action stop
```

Para detener:

- Doble click en `stop_portable_silent.vbs`

En `SistemasLaHuellaPortableTotal` el flujo es el mismo.

En el primer arranque de `SistemasLaHuellaPortableTotal`, el sistema intenta crear automaticamente en el escritorio:
- `Sistemas La Huella`
- `Detener Sistemas La Huella`

Si queres forzarlo manualmente:
- ejecutar `Instalar en Escritorio.bat`

## 3) Requisitos minimos en la PC destino

- Windows 10/11 o Windows Server 2019
- Python 3.x accesible por comando `py`
- Dependencias Python instaladas para la API:

```powershell
py -3 -m pip install -r requirements-api.txt
```

Para `SistemasLaHuellaPortableTotal`, estos requisitos no aplican.

## 4) Notas operativas

- El frontend se sirve estatico desde `frontend\dist`.
- La API corre en `127.0.0.1:8000`.
- El dashboard usa `http://localhost:8000/api` por defecto.
- Logs:
  - `portable.api.log`
  - `portable.api.err.log`
  - `portable.web.log`
  - `portable.web.err.log`
- PIDs:
  - `.run\lahuella-portable-api.pid`
  - `.run\lahuella-portable-web.pid`
- En modo portable total, los procesos se ejecutan desde:
  - `runtime\api\lahuella-api-portable.exe`
  - `runtime\web\lahuella-web-portable.exe`
