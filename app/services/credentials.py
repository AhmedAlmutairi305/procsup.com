"""Credential provider abstraction.

Default implementation reads from environment variables or prompts operator externally.
It intentionally avoids storing plaintext credentials in source code or database.
"""

import os


class CredentialProvider:
    def get_username(self, university_slug: str) -> str | None:
        return os.getenv(f"APP_USER_{university_slug.upper()}")

    def get_password(self, university_slug: str) -> str | None:
        return os.getenv(f"APP_PASS_{university_slug.upper()}")
