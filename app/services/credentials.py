"""Credential provider abstraction with keyring-first fallback."""

from app.services.secrets import secret_provider


class CredentialProvider:
    def get_username(self, university_slug: str) -> str | None:
        return secret_provider.get_secret("portal_user", university_slug)

    def get_password(self, university_slug: str) -> str | None:
        return secret_provider.get_secret("portal_pass", university_slug)
