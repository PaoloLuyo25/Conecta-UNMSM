# Publicar Conecta UNMSM en un repositorio GitHub vacío

Esta entrega contiene la **base integradora** (código de los tres módulos, agentes, documentación SDD, pruebas, SQL y fuentes revisadas). El archivo `.env` con credenciales no se incluye.

1. Extrae `Conecta UNMSM.zip` en tu equipo; tendrás la carpeta `conecta-unmsm`. Si ya trabajas en `C:\Users\josem\Downloads\conecta-unmsm-v4_4`, haz copia de la carpeta y del `.env` antes de migrar los archivos.
2. Abre CMD en la carpeta raíz (donde están `README.md`, `backend/` y `frontend/`).
3. Ejecuta:

```bat
cd /d "C:\Users\josem\Downloads\conecta-unmsm"
git init
git branch -M main
git add .
git status --short
git commit -m "Base integradora Conecta UNMSM"
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Reemplaza la URL por la del repositorio vacío de tu equipo. **Si `git remote -v` ya muestra `origin`, NO repitas `git remote add`; usa el remoto existente.** GitHub puede pedir autenticación con navegador/credencial personal, no pega un password o token en el código. Evita `git push --force`.

Antes del `git add` verifica que **no** aparezcan `.env`, `.venv`, tokens, respaldos de base o archivos personales. Si tienes una rama principal con contenido, haz `git pull` y reconcilia antes de publicar. Confirma las bases del hackathon sobre código preparado antes del evento.

No se puede efectuar el push desde este ZIP sin la URL del repositorio y acceso a GitHub autorizado.
