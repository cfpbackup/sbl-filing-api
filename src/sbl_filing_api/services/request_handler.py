import logging

import httpx
from sbl_filing_api.config import settings
from fastapi import status
from regtech_api_commons.api.exceptions import RegTechHttpException

logger = logging.getLogger(__name__)

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
    try:
        res = httpx.post(settings.mail_api_url, json=confirmation_request)
        if res.status_code != 200:
            logger.error(res.text)
    except Exception:
        logger.exception(f"Failed to send confirmation email for {user_full_name}")
