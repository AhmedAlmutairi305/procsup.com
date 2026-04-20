from __future__ import annotations

import os

try:
    import keyring
except Exception:  # pragma: no cover - optional dependency
    keyring = None


class SecretProvider:
    def get_secret(self, namespace: str, key: str) -> str | None:
        if keyring is not None:
            value = keyring.get_password(namespace, key)
            if value:
                return value
        return os.getenv(f"{namespace}_{key}".upper())


secret_provider = SecretProvider()
