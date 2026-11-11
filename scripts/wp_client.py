import os

import requests
import truststore
from dotenv import load_dotenv

# Usa los certificados de Windows (necesario detrás de proxies corporativos).
truststore.inject_into_ssl()
load_dotenv()


class WP:
    def __init__(self, prefix):
        self.base = os.getenv(f"{prefix}_URL").rstrip("/")
        user = os.getenv(f"{prefix}_USER")
        pwd = os.getenv(f"{prefix}_APP_PASSWORD")
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "WebAluminio-tools/1.0"
        self.has_credentials = bool(user and pwd)
        self.auth = False
        self.auth_error = "sin credenciales en .env"
        if self.has_credentials:
            self.s.auth = (user, pwd)
            self.auth, self.auth_error = self._check_auth()

    def _check_auth(self):
        """Verifica que WordPress reconozca las credenciales (no solo que existan)."""
        r = self.s.get(f"{self.base}/wp-json/wp/v2/users/me", params={"context": "edit"}, timeout=60)
        if r.ok:
            caps = r.json().get("capabilities", {})
            if not caps.get("edit_others_posts"):
                return False, "el usuario no tiene permisos de editor/administrador"
            return True, ""
        code = r.json().get("code", r.status_code) if "json" in r.headers.get("Content-Type", "") else r.status_code
        if code == "rest_not_logged_in":
            return False, ("WordPress no recibe la cabecera Authorization (revisa .htaccess: "
                           'SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1)')
        if code in ("invalid_username", "incorrect_password"):
            return False, "usuario o contraseña de aplicación incorrectos"
        return False, f"error de autenticación: {code}"

    def status(self):
        return "sí" if self.auth else f"no ({self.auth_error})"

    def require_auth(self):
        if not self.auth:
            raise RuntimeError(f"{self.base}: se requieren credenciales válidas para escribir: {self.auth_error}")

    def get_all(self, endpoint, **params):
        """Recorre todas las páginas de un endpoint de wp/v2."""
        params = {"per_page": 100, **params}
        if self.auth and endpoint in ("posts", "pages", "portafolio"):
            params.setdefault("status", "any")
        items, page = [], 1
        while True:
            r = self.s.get(f"{self.base}/wp-json/wp/v2/{endpoint}", params={**params, "page": page}, timeout=60)
            if r.status_code == 400 and page > 1:
                break
            r.raise_for_status()
            items += r.json()
            if page >= int(r.headers.get("X-WP-TotalPages", 1)):
                break
            page += 1
        return items

    def update(self, endpoint, item_id, data):
        self.require_auth()
        r = self.s.post(f"{self.base}/wp-json/wp/v2/{endpoint}/{item_id}", json=data, timeout=60)
        r.raise_for_status()
        return r.json()


old = lambda: WP("OLD")
new = lambda: WP("NEW")


if __name__ == "__main__":
    # python scripts/wp_client.py -> valida el .env sin mostrar credenciales
    for site in (old(), new()):
        print(f"{site.base}: autenticado={site.status()}")
