# Plan Mejora 2 (pendiente)

Estado: pendiente.  
Se ejecuta al finalizar la funcionalidad de "Infraestructura por vía".

## 1) Modo cabina completo
- Header y toolbar fijos (`sticky`).
- Tabla principal con mayor alto útil y scroll interno estable.
- KPIs críticos siempre visibles (listos, sin conexión, fallo auth).

## 2) Alertas operativas
- Reglas base: host caído, auth fail, puerto cerrado.
- Aviso visual persistente + sonido opcional.
- Opción de silenciado temporal por operador (ej. 15 min).

## 3) Historial y auditoría
- Registro de acciones por host (qué, cuándo, resultado).
- Filtros por fecha, host, tipo de evento.
- Exportación CSV/JSON.

## 4) Plantillas operativas por grupo
- Perfiles por conjunto de vías (ej. 51-55, 07-11).
- Comandos/rutas predefinidas.
- Ejecución por lote con confirmación.

## 5) Seguridad base
- Evitar persistencia de secretos en frontend.
- Endurecer manejo de variables sensibles en backend/entorno.
- Restringir acciones sensibles por rol (reinicio/rotación).

## 6) Resiliencia de red
- Reintentos con backoff.
- Timeouts por tipo de operación.
- Descubrimiento automático de subred activa + fallback.
