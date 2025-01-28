import os
import random
import logging
from datetime import datetime

from time import sleep
from typing import Any, Dict
from requests.adapters import HTTPAdapter

from locust import HttpUser, FastHttpUser, task, between
from startup import startup, refresh_token
from shutdown import shutdown

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

process_complete = ["UPLOAD_FAILED", "VALIDATION_ERROR", "VALIDATION_SUCCESSFUL", "VALIDATION_WITH_ERRORS", "VALIDATION_WITH_WARNINGS"]

class FilingApiUser(HttpUser):
    tokens: Dict[str, Any]
    last_token_refresh: datetime
    user_id: str
    lei: str
    period_code: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.verify = False
        # self.client.mount('https://', HTTPAdapter(pool_maxsize=50))
        # self.client.mount('http://', HTTPAdapter(pool_maxsize=50))

    @task
    def submit_sblar(self):
        self.refresh_tokens()
        sblar_dir = os.getenv("SBLAR_LOCATION", "./locust-load-test/sblars")
        sblar = random.choice(os.listdir(sblar_dir))
        start = datetime.now()
        sub_counter = self.client.post(
            f"/v1/filing/institutions/{self.lei}/filings/{self.period_code}/submissions",
            files=[("file", (sblar, open(os.path.join(sblar_dir, sblar), "rb"), "text/csv"))],
        ).json()["counter"]
        sleep(2)
        status = None
        while status not in process_complete:
            self.refresh_tokens()
            status = self.client.get(
                f"/v1/filing/institutions/{self.lei}/filings/{self.period_code}/submissions/{sub_counter}",
            ).json()["state"]
            now = datetime.now()
            elapsed_mins = int((now - start).total_seconds()) / 60
            if elapsed_mins > 15:
                break
            sleep(1)
        logger.info(f"processed {sblar} in {(datetime.now() - start).total_seconds()} seconds. status: {status}")

    # def on_stop(self):
    #     shutdown(self.user_id)

    def on_start(self):
        user_id, tokens, lei = startup()
        self.user_id = user_id
        self.tokens = tokens
        self.last_token_refresh = datetime.now()
        self.lei = lei
        self.client.headers = {"Authorization": "Bearer " + self.tokens["access_token"]}
        self.get_filing_periods()
        self.create_filing()

    def get_filing_periods(self):
        response = self.client.get(
            "/v1/filing/periods"
        )
        periods = response.json()
        sorted_periods = sorted(periods, key=lambda p: p["due"], reverse=True)
        self.period_code = sorted_periods[0]["code"]

    
    def create_filing(self):
        self.client.post(
            f"/v1/filing/institutions/{self.lei}/filings/{self.period_code}"
        )
    
    def refresh_tokens(self):
        now = datetime.now()
        if int((now - self.last_token_refresh).total_seconds()) / 60 > 5:
            self.tokens = refresh_token(self.tokens["refresh_token"])
            self.last_token_refresh = now
            self.client.headers = {"Authorization": "Bearer " + self.tokens["access_token"]}
