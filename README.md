# Actualizaciones de IsaVal POS

Este repositorio distribuye exclusivamente APK firmados y sus manifiestos. El código y la clave de firma permanecen en el repositorio privado.

Canal estable para la app:
https://github.com/juamario-ux/isaval-pos-updates/releases/latest/download/version.json

## Publicar una nueva versión
1. Incrementar versionCode y versionName en el repositorio privado alpha-0.2 y obtener una compilación exitosa.
2. Obtener el enlace temporal de descarga del ZIP de Actions mediante el conector GitHub. No utilizar el enlace de la página web del artefacto.
3. Ejecutar Actions → Publish verified IsaVal POS update → Run workflow; ingresar la URL temporal y las notas.
4. El publicador verifica criptográficamente el APK y su certificado de IsaVal, extrae paquete/versión, rechaza retrocesos, calcula SHA-256 y publica APK + version.json antes de promover Latest.
5. Desde IsaVal POS pulsar Buscar actualización → Descargar → Instalar y confirmar la instalación Android. Las ventas guardadas se conservan.

No hace falta conectar la SUNMI por USB para las versiones siguientes.
La publicación requiere un operador después de compilar. No se publica automáticamente cada push del repositorio privado.
No se necesitan tokens personales ni se guardan credenciales en la app.
