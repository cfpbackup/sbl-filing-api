import asyncio
import logging

from concurrent.futures import ProcessPoolExecutor
from fastapi import BackgroundTasks
from multiprocessing import Manager
from sbl_filing_api.config import settings
from sbl_filing_api.entities.models.dao import SubmissionDAO
from sbl_filing_api.entities.repos import submission_repo as repo
from sbl_filing_api.services.submission_processor import validate_and_update_submission
from sqlalchemy.ext.asyncio import AsyncSession

class MultithreadedSubmissionHandler():
    
    def __init__(self,
                 background_tasks: BackgroundTasks,
                 session: AsyncSession):
        self.background_tasks = background_tasks
        self.exec_check = Manager().dict()
        self.session = session
        self.logger = logging.getLogger(__name__)
        
    
    def handle_submission(self, period_code: str, lei: str, submission: SubmissionDAO, content: bytes):
        self.exec_check['continue'] = True
        executor = ProcessPoolExecutor()
        future = executor.submit(self.validate_submission, period_code, lei, submission, content)
        self.background_tasks.add_task(self.check_future, future, submission.id)
        executor.shutdown(wait=False)
        
        
    def validate_submission(self, period_code: str, lei: str, submission: SubmissionDAO, content: bytes):
        loop = asyncio.new_event_loop()
        try:
            coro = validate_and_update_submission(period_code, lei, submission, content, self.exec_check, self.session)
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
        except Exception as e:
            self.logger.error(e, exc_info=True, stack_info=True)
        finally:
            loop.close()
    
    
    async def check_future(self, future, submission_id):
        await asyncio.sleep(settings.expired_submission_check_secs)
        if not future.done():
            self.exec_check['continue'] = False
            await repo.expire_submission(submission_id, self.session)
            self.logger.warn(f"Validation for submission {submission_id} did not complete within the expected timeframe, will be set to VALIDATION_EXPIRED.")