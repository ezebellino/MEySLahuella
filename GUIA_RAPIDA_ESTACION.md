# Guia Rapida - Estacion de Peaje

## 1. Inicio rapido

1. Conectar el pendrive.
2. Abrir la carpeta `SistemasLaHuellaPortableTotal`.
3. Ejecutar `start_portable_silent.vbs`.
4. Esperar unos segundos.
5. Abrir en el navegador: `http://127.0.0.1:5173`

## 2. Accesos directos de escritorio

- En el primer arranque, el sistema intenta crear automaticamente:
  - `Sistemas La Huella`
  - `Detener Sistemas La Huella`
- Si no aparecen, ejecutar:
  - `Instalar en Escritorio.bat`

## 3. Uso basico

- Revisar el panel principal.
- Verificar host local, servidor objetivo y subred.
- Ejecutar chequeos de red y hosts.
- Validar credenciales si corresponde.
- Consultar alertas operativas y auditoria.

## 4. Cierre correcto

1. Ejecutar `stop_portable_silent.vbs`
2. Esperar unos segundos.
3. Retirar el pendrive de forma segura.

## 5. Archivos utiles

- `check_estacion_peaje.md`: checklist imprimible
- `validacion_estacion_peaje.md`: planilla de validacion
- `PORTABLE_PENDRIVE.md`: guia tecnica del modo portable

## 6. Si algo falla

- Revisar:
  - `portable.api.log`
  - `portable.api.err.log`
  - `portable.web.log`
  - `portable.web.err.log`
- Si los accesos directos no aparecen, correr `Instalar en Escritorio.bat`
- Si la app no abre, relanzar `start_portable_silent.vbs`
