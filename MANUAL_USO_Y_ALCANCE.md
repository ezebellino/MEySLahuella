# Sistemas La Huella - Manual de Uso y Alcance

Fecha de referencia: 2026-04-16  
Documento vivo: **SI** (debe actualizarse con cada mejora funcional o cambio de flujo)

## 1. Objetivo de la aplicación

Centralizar desde un único dashboard la operación local y la administración remota de hosts, especialmente entornos Windows Server (incluyendo Windows Server 2019), con foco en:

- Diagnóstico de red.
- Gestión de hosts remotos.
- Validación de credenciales.
- Operaciones remotas de archivos/comandos.

## 2. Alcance funcional actual

### 2.1 Operación local
- Consulta y actualización de parámetros de antena.
- Movimiento de archivos `.dat`.
- Visualización de estado de archivos de tags.

### 2.2 Gestión de hosts
- Alta, edición y baja de hosts.
- Asociación de nombre amigable por host.
- Soporte por IP o DNS.
- Soporte de `host_type` (`windows` / `linux`).

### 2.3 Diagnóstico de red
- Escaneo de subred por puerto configurable.
- Test rápido por host (conectividad y estado).
- Test rápido global de todos los hosts.

### 2.4 Credenciales
- Prueba de múltiples candidatos de usuario/contraseña por host.
- Resultado `OK/FAIL` por credencial.
- Guardado automático de credencial válida al host (si aplica).
- Rotación de credencial por host en un solo flujo:
  - Actualiza usuario/contraseña.
  - Verifica autenticación inmediatamente.
  - Si falla, revierte automáticamente a la credencial anterior.
- Historial de rotaciones por host:
  - Registro de intentos, éxito/fallo, rollback y timestamp.

### 2.5 Operación remota
- Listado de archivos remotos.
- Ejecución de comando remoto.
- Reinicio remoto (según comando configurado).
- Transferencia de texto (subida/bajada).

### 2.6 UX del dashboard
- Flujo por pasos:
  1) Red y Diagnóstico  
  2) Hosts y Credenciales  
  3) Operación Remota
- Tabla de hosts con filtros.
- Semáforos de estado (SMB/WinRM/Auth).
- KPIs operativos.
- Exportación CSV del estado de hosts.

## 3. Alcance técnico

### 3.1 Backend
- API en Python (FastAPI).
- Persistencia local de hosts en `data/hosts.json`.
- Credenciales protegidas en reposo:
  - Windows: cifrado DPAPI (vinculado al usuario/maquina que cifra).
  - No-Windows: fallback codificado (`plain:`) para compatibilidad de entorno.
- Operación remota orientada a Windows (SMB/WinRM) y compatibilidad Linux (SSH).

### 3.2 Frontend
- React + Vite.
- Estado de filtros/paso persistido localmente (`localStorage`).

### 3.3 Ejecución
- Inicio/parada manual y modo silencioso en segundo plano:
  - `start_app_silent.vbs`
  - `stop_app_silent.vbs`
- Archivos PID en `.run/` para control de procesos.

## 4. Fuera de alcance (actual)

- Gestión de usuarios/roles por perfil dentro del dashboard.
- Integración con un gestor central de secretos (Vault/KMS corporativo).
- Inventario automático por Active Directory.
- Auditoría avanzada centralizada (SIEM/externa).

## 5. Supuestos y dependencias

- Conectividad de red real al segmento objetivo.
- Puertos de administración habilitados según protocolo.
- Credenciales válidas para el servicio/protocolo usado.
- Resolución DNS correcta si se usan nombres en lugar de IP.

## 6. Riesgos operativos

- Timeout o bloqueos por red/VPN/rutas.
- Errores de autenticación por formato de usuario o contraseña.
- Diferencias entre permisos de usuario para SMB/WinRM/RDP.

## 7. Política de actualización de este documento (obligatoria)

Cada mejora debe reflejarse en este archivo antes de cerrar el cambio.

Checklist mínimo por actualización:

1. Actualizar `Fecha de referencia`.
2. Agregar/editar alcance funcional afectado.
3. Agregar “fuera de alcance” si cambió.
4. Registrar cambios en la sección de historial.

## 8. Historial de cambios del manual

- 2026-04-16:
  - Creación inicial del manual.
  - Definición de alcance funcional, técnico y límites.
  - Definición de política obligatoria de actualización.
- 2026-04-16 (actualización):
  - Se agrega cifrado de credenciales en reposo con DPAPI en Windows.
  - Se agrega rotación de credenciales con verificación y rollback.
  - Se agrega historial de rotaciones con consulta por host.
- 2026-04-16 (actualizacion 2):
  - Se agrega modo compacto y modo cabina para monitoreo continuo.
  - Se agrega panel de alertas operativas (host offline, auth fail, SMB/WinRM cerrado), con silencio temporal.
  - Se agrega infraestructura por via (switch + antena/pc/impresora/camaras) con persistencia por host.
  - Se agrega historial y auditoria de eventos con filtros y exportacion CSV/JSON.
  - Se agregan plantillas operativas por grupo de vias y ejecucion por lote con confirmacion.
  - Seguridad base:
    - Guardia critica para acciones sensibles (reinicio, rotacion, borrado de host y lote).
    - Confirmacion por palabra clave para acciones sensibles.
    - Limpieza de contrase�as temporales en frontend tras pruebas/rotaciones.
    - Plantillas persistidas sin contenido sensible (sin comando ni payload de transferencia).
- 2026-04-16 (actualizacion 3):
  - Resiliencia de red en frontend API: timeouts por operacion y reintentos con backoff.
  - Indicador de 'via reintento' en resultados de monitoreo/comando/transferencia/lote.
  - Deteccion de subred con fallback (local + 10.95.25.0/24 + 192.168.2.0/24).
