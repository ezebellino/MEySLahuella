# Planilla de Validacion - Sistemas La Huella

Fecha: ____ / ____ / ______  
Operador: __________________  
Estacion / Via: ____________  
Version app: _______________

| Paso | Resultado esperado | OK/FAIL | Observacion |
|---|---|---|---|
| 1. Ejecutar `start_portable_silent.vbs` | La app inicia sin abrir terminales |  |  |
| 2. Verificar health API | `http://127.0.0.1:8000/api/health` responde 200 |  |  |
| 3. Abrir dashboard | `http://127.0.0.1:5173` carga correctamente |  |  |
| 4. Detectar subred actual | La subred visible coincide con la red de trabajo |  |  |
| 5. Escanear SMB 445 | El escaneo finaliza sin error |  |  |
| 6. Ver servidor principal | `10.95.25.10` aparece en el panel |  |  |
| 7. Ver vias objetivo | Hosts Via 51/52/53/54/55/07/08/09/10/11 visibles |  |  |
| 8. Probar credencial usuario `via` | Autenticacion correcta en host de prueba |  |  |
| 9. Probar credencial `administrator` | Autenticacion correcta en host de prueba |  |  |
| 10. Ejecutar operacion de archivos | Se lista o transfiere archivo segun accion |  |  |
| 11. Ejecutar comando remoto controlado | Comando responde sin error |  |  |
| 12. Probar alerta operativa | Se visualiza alerta en panel |  |  |
| 13. Probar silenciado de alerta | Alerta queda silenciada segun configuracion |  |  |
| 14. Verificar auditoria | Evento registrado con host, accion y resultado |  |  |
| 15. Exportar eventos CSV/JSON | Archivo exportado disponible |  |  |
| 16. Guardar infraestructura de via | Mapa de puntos (antena/PC/impresora/camaras) guardado |  |  |
| 17. Ejecutar `stop_portable_silent.vbs` | Sistema se detiene sin dejar procesos activos |  |  |

## Firma de conformidad

Responsable: ______________________  
Firma: ____________________________  
Fecha: ____ / ____ / ______

