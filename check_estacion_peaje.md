# Checklist Operativo - Estacion de Peaje (Imprimible)

Fecha: ____ / ____ / ______  
Turno: ____________________  
Operador: __________________  
Estacion / Via: ____________  
Version app: _______________

## 1. Preparacion

- [ ] Pendrive conectado y detectado
- [ ] Carpeta `SistemasLaHuellaPortable` visible
- [ ] PC de la estacion con red operativa
- [ ] Hora/fecha de la PC correctas
- [ ] Usuario con permisos suficientes

## 2. Inicio del sistema

- [ ] Ejecutado `start_portable_silent.vbs` (doble click)
- [ ] API responde en `http://127.0.0.1:8000/api/health`
- [ ] Dashboard abre en `http://127.0.0.1:5173`
- [ ] Sin errores visibles de carga en pantalla

## 3. Red y diagnostico

- [ ] Subred detectada automaticamente
- [ ] Objetivo servidor principal correcto (`10.95.25.10`)
- [ ] Escaneo SMB (445) ejecutado
- [ ] Hosts objetivo aparecen en listado
- [ ] Estado de tags visible/actualizable

## 4. Hosts y credenciales

- [ ] Hosts de vias cargados (Via 51, 52, 53, 54, 55, 07, 08, 09, 10, 11)
- [ ] Prueba de credencial `via` completada
- [ ] Prueba de credencial `administrator` completada
- [ ] Resultado de autenticacion guardado en auditoria
- [ ] Fallback de credenciales funciona si la primaria falla

## 5. Operacion remota

- [ ] Listado de archivos remoto accesible
- [ ] Operacion de mover/transferir `.dat` validada
- [ ] Comando remoto de reinicio probado (entorno controlado)
- [ ] Operacion remota deja registro en auditoria

## 6. Alertas y guardia critica

- [ ] Alertas activas visibles (si corresponde)
- [ ] Boton de silenciar/reactivar operativo
- [ ] Modo guardia critica evaluado
- [ ] Sonido/indicadores se comportan segun configuracion

## 7. Infraestructura de via

- [ ] Mapa de switch por host cargado/actualizado
- [ ] Antena TelePASE documentada
- [ ] PC de via documentada
- [ ] Impresora documentada
- [ ] Camara vigilancia documentada
- [ ] Camara OCR documentada

## 8. Cierre

- [ ] Export CSV/JSON (si aplica) generado
- [ ] Evidencia guardada (capturas/logs)
- [ ] Ejecutado `stop_portable_silent.vbs`
- [ ] Verificado: no quedan procesos abiertos
- [ ] Pendrive retirado en forma segura

## Observaciones generales

____________________________________________________________________________

____________________________________________________________________________

____________________________________________________________________________

