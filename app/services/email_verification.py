from __future__ import annotations

import imaplib
import email
import re
from datetime import datetime

from app.services.secrets import secret_provider


def poll_verification_email(email_address: str, password_reference: str, imap_server: str, mailbox: str = "INBOX") -> dict:
    password = secret_provider.get_secret("email", password_reference)
    if not password:
        return {"status": "missing_credentials", "message": "No email password found in keyring/env"}

    try:
        with imaplib.IMAP4_SSL(imap_server) as client:
            client.login(email_address, password)
            client.select(mailbox)
            status, data = client.search(None, '(UNSEEN SUBJECT "verification")')
            if status != "OK" or not data or not data[0]:
                return {"status": "waiting", "checked_at": datetime.utcnow().isoformat()}

            latest_id = data[0].split()[-1]
            _, msg_data = client.fetch(latest_id, "(RFC822)")
            raw = msg_data[0][1]
            parsed = email.message_from_bytes(raw)
            body = ""
            if parsed.is_multipart():
                for part in parsed.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = parsed.get_payload(decode=True).decode(errors="ignore")

            code = re.search(r"\b(\d{4,8})\b", body)
            link = re.search(r"https?://\S+", body)
            return {
                "status": "found",
                "code": code.group(1) if code else None,
                "link": link.group(0) if link else None,
                "subject": parsed.get("subject"),
                "checked_at": datetime.utcnow().isoformat(),
            }
    except Exception as exc:
        return {"status": "error", "message": str(exc), "checked_at": datetime.utcnow().isoformat()}
