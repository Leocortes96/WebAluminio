# WebAluminio

Herramientas para migrar y optimizar los sitios WordPress:

- **Antiguo:** https://www.imperioaluminio.com (funcionaba con Google Ads)
- **Nuevo:** https://www.disenosyproyectos.com

## Configuración

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env   # completa usuario y contraseña de aplicación
```

Sin credenciales, los scripts solo leen el contenido público.

## Scripts

| Script | Qué hace |
|---|---|
| `python scripts/wp_client.py` | Valida el `.env` en ambos sitios sin mostrar las credenciales |
| `python scripts/inventario.py` | Inventario de ambos sitios, comparativo de URLs (faltantes / redirecciones 301) e imágenes sin `alt` en `data/` |
| `python scripts/redirecciones.py generar` | Valida `redirecciones.csv` y crea `data/redirection_import.csv` para el plugin Redirection |
| `python scripts/redirecciones.py verificar` | Comprueba que cada URL antigua responda 301 directo al destino y que el destino responda 200 |
| `python scripts/alt_imagenes.py contexto` | Mapea en qué páginas se usa cada imagen (`data/alt_contexto.csv`) |
| `python scripts/alt_imagenes.py dry-run` | Muestra los cambios de `data/alt_propuesto.csv` frente al alt actual |
| `python scripts/alt_imagenes.py aplicar` | Respalda en `data/backup/`, pide confirmar con `APLICAR` y escribe los alt |
| `python scripts/alt_imagenes.py restaurar <json>` | Revierte los alt desde un respaldo |

## Reglas de escritura

Antes de escribir en un sitio, el script respalda en `data/backup/` y muestra un dry-run. No se aplica nada sin aprobación. Al terminar, purga la caché de LiteSpeed.

## Autenticación (bloqueo actual)

Ambos sitios responden `401 rest_not_logged_in` incluso con credenciales, porque LiteSpeed elimina la cabecera `Authorization`. Para corregirlo:

1. En el `.htaccess` de cada sitio, encima de `# BEGIN WordPress`, agrega:
   `SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1`
2. En el `.env`, usa una **contraseña de aplicación** de 24 caracteres (Usuarios › Perfil › Contraseñas de aplicación), no la contraseña de inicio de sesión.
3. Corre `python scripts/wp_client.py` y luego `python scripts/inventario.py`, que ya incluirá los borradores.

## Estado por tarea

1. **Inventario:** se ejecutó con datos públicos (18 contenidos en el antiguo y 20 en el nuevo; 144 de 144 imágenes sin alt). Faltan los borradores, que requieren autenticación.
2. **Redirecciones:** `data/redirection_import.csv` está listo, pero 2 destinos siguen por confirmar (`instalaciones-y-asesorias` y `pasamanos`). Hoy funcionan bien 2 de 8. Para completarlo:
   1. Importa el CSV en Herramientas › Redirection › Importar. No uses el importador *old post slugs*.
   2. Purga la caché de LiteSpeed.
   3. Corre `verificar`. El resultado debe ser 8 de 8.
3. **Imágenes:** el dry-run de `data/alt_propuesto.csv` está listo y cambia 92 alt. Además, 8 imágenes decorativas quedan vacías, 40 de plantilla se recomiendan para eliminar y 4 se omiten. Para aplicarlo hacen falta tu aprobación y la autenticación.
4. **Portafolios:** las propuestas de los 12 portafolios están en `docs/tarea4_portafolio_seo.md` y `data/portafolio_seo_propuesto.csv`. No hay plugin de SEO; se recomienda **Rank Math (gratis)**. Los textos de Elementor no se pueden editar de forma segura por la API, así que se recomienda pegarlos a mano.
5. **Google Ads:** la comparación de landings, el checklist de GA4, GTM y conversiones, y la estructura de campañas están en `docs/tarea5_google_ads.md`. Hoy no se mide ninguna conversión y el contenedor GTM es compartido entre los dos sitios.
