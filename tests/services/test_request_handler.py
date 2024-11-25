import pytest
from unittest.mock import ANY
from regtech_api_commons.api.exceptions import RegTechHttpException
from pytest_mock import MockerFixture
from sbl_filing_api.services.request_handler import send_confirmation_email


def test_send_confirmation_email(mocker: MockerFixture):
    post_mock = mocker.patch("sbl_filing_api.services.request_handler.httpx.post")
    send_confirmation_email("full_name", "user@email.com", "contact@info.com", "confirmation", 12345)

    post_mock.assert_called_with(
        ANY,
        json={
            "confirmation_id": "confirmation",
            "contact_email": "contact@info.com",
            "signer_email": "user@email.com",
            "signer_name": "full_name",
            "timestamp": 12345,
        },
    )

    post_mock.side_effect = IOError("test")
    with pytest.raises(Exception) as e:
        send_confirmation_email("full_name", "user@email.com", "contact@info.com", "confirmation", 12345)
    assert isinstance(e.value, RegTechHttpException)
    assert e.value.status_code == 503
    assert e.value.name == "Confirmation Email Send Fail"
    assert e.value.detail == "Failed to send confirmation email for user@email.com."
