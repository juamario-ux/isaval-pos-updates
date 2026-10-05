# Actualizaciones de IsaVal POS

Canal estable:
https://github.com/juamario-ux/isaval-pos-updates/releases/latest/download/version.json

Este repositorio distribuye APK firmados y manifiestos. El código de la app y la clave de firma permanecen privados.

## Publicar una nueva versión
1. Incrementar versionCode y versionName en la rama alpha-0.2 del repositorio privado y obtener una compilación exitosa.
2. Descargar el APK de GitHub Actions.
3. Crear un borrador de Release aquí con etiqueta vVERSION-buildCODIGO (por ejemplo v0.2.2-build8) y adjuntar el APK firmado.
4. Ejecutar Actions → Publish verified IsaVal POS update → Run workflow; indicar la etiqueta del borrador y las notas.
5. El publicador valida firma criptográfica, certificado de IsaVal, applicationId y versión; rechaza retrocesos, calcula SHA-256 y agrega version.json antes de promover el borrador a Latest.
6. Desde la SUNMI: Buscar actualización → Descargar → Instalar; confirmar la instalación Android.

Cada próxima versión se publica en este mismo canal. La SUNMI no necesita USB.
La publicación requiere un operador después de compilar; cada push privado no se publica automáticamente.
El publicador usa únicamente el GITHUB_TOKEN temporal de este repositorio. La app no contiene credenciales.
