# Peaje - Mini Aplicación de Gestión de Archivos e Información

Este proyecto es una aplicación gráfica desarrollada en Python que permite:
1. **Mover archivos** con extensión `.dat` desde una carpeta de origen hacia una carpeta de destino, creando automáticamente una subcarpeta con fecha única.
2. **Gestionar información de antenas**:
   - Leer y mostrar los valores de `REMOTE_HOST` (dirección IP) y `POTENCIA` desde un archivo de configuración `TciNumero.ini`.
   - Editar fácilmente el valor de `POTENCIA` directamente desde la interfaz gráfica.

---

## **Características**
- **Interfaz gráfica intuitiva**: Diseñada con Tkinter, incluye una interfaz moderna y fácil de usar.
- **Automatización del manejo de archivos**:
  - Busca y mueve todos los archivos `.dat` desde una carpeta de origen hacia una subcarpeta con fecha única.
  - Garantiza que no haya conflictos de nombres de subcarpetas gracias a un sistema de numeración automática (por ejemplo, `25.01.25`, `25.01.25-2`).
- **Edición sencilla de configuraciones**:
  - Visualiza y modifica parámetros del archivo `TciNumero.ini` ubicado en `C:\Windows\`.

---

## **Requisitos del sistema**
Para ejecutar esta aplicación necesitas:
- **Sistema operativo**: Windows 10 o superior.
- **Python**: No es necesario si utilizas el archivo ejecutable (.exe).
- **Archivo de configuración**: `TciNumero.ini` debe existir en la ruta `C:\Windows\` y contener la sección `[ANTENA_UIP]`.

---

## **Instrucciones de uso**

### **1. Descargar y ejecutar**
1. Descarga el archivo ejecutable `Interfaz.exe` desde la carpeta `dist/`.
2. Coloca el ejecutable en cualquier ubicación de tu preferencia (incluso en un pendrive).
3. Haz doble clic en `Interfaz.exe` para abrir la aplicación.

### **2. Mover archivos `.dat`**
1. En la sección **"Mover Archivos"**:
   - Selecciona la carpeta de origen que contiene los archivos `.dat`.
   - Selecciona la carpeta de destino donde se crearán las subcarpetas.
   - Haz clic en el botón **"Mover Archivos"**.
2. Los archivos `.dat` serán movidos a una subcarpeta con la fecha actual. Si ya existe una carpeta con esa fecha, se creará otra con un sufijo numérico (`-2`, `-3`, etc.).

### **3. Gestión de información de antenas**
1. En la sección **"Configuración de Antena"**:
   - Haz clic en **"Mostrar Datos"** para ver los valores actuales de `REMOTE_HOST` y `POTENCIA`.
   - Si deseas cambiar la potencia:
     - Ingresa el nuevo valor en el campo de texto.
     - Haz clic en el botón **"Actualizar Potencia"**.
2. El valor de `POTENCIA` se actualizará en el archivo `TciNumero.ini` y se reflejará al volver a consultar los datos.

---

## **Preguntas frecuentes**

### **1. ¿Es esta aplicación portable?**
Sí, el ejecutable generado es completamente portable:
- Puedes llevar el archivo `.exe` en un pendrive o carpeta.
- Funciona en cualquier PC con Windows 10 o superior, siempre que:
  - El archivo de configuración `TciNumero.ini` exista en la ruta `C:\Windows\`.
  - El antivirus no bloquee el ejecutable (puedes agregarlo a la lista de excepciones si es necesario).

### **2. ¿Qué ocurre si no hay archivos `.dat` en la carpeta de origen?**
La aplicación mostrará un mensaje indicando que no hay archivos para mover.

### **3. ¿Qué ocurre si `TciNumero.ini` no existe o no contiene `[ANTENA_UIP]`?**
La aplicación mostrará un error indicando que el archivo o la sección no se encontraron.

---

## **Cómo contribuir**
Si deseas contribuir a este proyecto:
1. Haz un fork del repositorio: [https://github.com/ezebellino/MEySLaHuella](https://github.com/ezebellino/MEySLaHuella).
2. Crea una nueva rama para tus cambios:
   ```bash
   git checkout -b nueva-funcionalidad
