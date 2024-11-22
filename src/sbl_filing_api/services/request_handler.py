from datetime import datetime

import httpx
from sbl_filing_api.config import settings


def send_confirmation_email(
    user_full_name: str, user_email: str, contact_info_email: str, confirmation_id: str, timestamp: int
):
    confirmation_request = {
        "confirmation_id": confirmation_id,
        "signer_email": user_email,
        "signer_name": user_full_name,
        "contact_email": contact_info_email,
        "timestamp": timestamp,
    }
    res = httpx.post(settings.mail_api_url, json=confirmation_request)
    return res
