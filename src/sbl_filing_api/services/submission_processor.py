from typing import Generator

# import pandas as pd
# import importlib.metadata as imeta
import logging

# from io import BytesIO
from fastapi import UploadFile

# from regtech_data_validator.create_schemas import validate_phases
# from regtech_data_validator.data_formatters import df_to_dicts, df_to_download
# from regtech_data_validator.checks import Severity
# from regtech_data_validator.validation_results import ValidationResults, ValidationPhase
# from sbl_filing_api.entities.engine.engine import SessionLocal
# from sbl_filing_api.entities.models.dao import SubmissionDAO, SubmissionState
# from sbl_filing_api.entities.repos import submission_repo as repo
from http import HTTPStatus
from sbl_filing_api.config import settings
from sbl_filing_api.services import file_handler
from regtech_api_commons.api.exceptions import RegTechHttpException

# from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)

REPORT_QUALIFIER = "_report"


def validate_file_processable(file: UploadFile) -> None:
    extension = file.filename.split(".")[-1].lower()
    if file.content_type != settings.submission_file_type or extension != settings.submission_file_extension:
        raise RegTechHttpException(
            status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            name="Unsupported File Type",
            detail=(
                f"Only {settings.submission_file_type} file type with extension {settings.submission_file_extension} is supported; "
                f'submitted file is "{file.content_type}" with "{extension}" extension',
            ),
        )
    if file.size > settings.submission_file_size:
        raise RegTechHttpException(
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            name="File Too Large",
            detail=f"Uploaded file size of {file.size} bytes exceeds the limit of {settings.submission_file_size} bytes.",
        )


def upload_to_storage(period_code: str, lei: str, file_identifier: str, content: bytes, extension: str = "csv") -> None:
    try:
        file_handler.upload(path=f"upload/{period_code}/{lei}/{file_identifier}.{extension}", content=content)
    except Exception as e:
        raise RegTechHttpException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, name="Upload Failure", detail="Failed to upload file"
        ) from e


def get_from_storage(period_code: str, lei: str, file_identifier: str, extension: str = "csv") -> Generator:
    try:
        return file_handler.download(f"upload/{period_code}/{lei}/{file_identifier}.{extension}")
    except Exception as e:
        raise RegTechHttpException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, name="Download Failure", detail="Failed to read file."
        ) from e


"""
async def validate_and_update_submission(
    period_code: str, lei: str, submission: SubmissionDAO, content: bytes, exec_check: dict
):
    async with SessionLocal() as session:
        try:
            from datetime import datetime
            start = datetime.now()
            validator_version = imeta.version("regtech-data-validator")
            submission.validation_ruleset_version = validator_version
            submission.state = SubmissionState.VALIDATION_IN_PROGRESS
            submission = await repo.update_submission(session, submission)
            v_start = datetime.now()
            df = pd.read_csv(BytesIO(content), dtype=str, na_filter=False)
            submission.total_records = len(df)

            # Validate Phases
            results = validate_phases(df, {"lei": lei}, max_errors=settings.max_validation_errors)
            log.error(f"V Processing took {(datetime.now() - v_start).total_seconds()} seconds")
            e_start = datetime.now()
            submission.validation_results = build_validation_results(results)

            if results.findings.empty:
                submission.state = SubmissionState.VALIDATION_SUCCESSFUL
            elif (
                results.phase == ValidationPhase.SYNTACTICAL
                or submission.validation_results["logic_errors"]["total_count"] > 0
            ):
                submission.state = SubmissionState.VALIDATION_WITH_ERRORS
            else:
                submission.state = SubmissionState.VALIDATION_WITH_WARNINGS

            submission_report = df_to_download(
                results.findings,
                warning_count=results.warning_counts.total_count,
                error_count=results.error_counts.total_count,
                max_errors=settings.max_validation_errors,
            )
            
            upload_to_storage(
                period_code, lei, str(submission.counter) + REPORT_QUALIFIER, submission_report.encode("utf-8")
            )
            log.error(f"E Processing took {(datetime.now() - e_start).total_seconds()} seconds")
            if not exec_check["continue"]:
                log.warning(f"Submission {submission.id} is expired, will not be updating final state with results.")
                return

            await repo.update_submission(session, submission)
            log.error(f"Processing took {(datetime.now() - start).total_seconds()} seconds")

        except RuntimeError:
            log.exception("The file is malformed.")
            submission.state = SubmissionState.SUBMISSION_UPLOAD_MALFORMED
            await repo.update_submission(session, submission)

        except Exception:
            log.exception("Validation for submission %d did not complete due to an unexpected error.", submission.id)
            submission.state = SubmissionState.VALIDATION_ERROR
            await repo.update_submission(session, submission)


def build_validation_results(submission: SubmissionDAO, session: AsyncSession):
    phase = repo.get_validation_phase(session, submission.id)

    findings = repo.get_findings(session, submission.id, settings.max_json_group_size)
    data = [r.__dict__ for r in findings]
    for d in data:
        d.pop("_sa_instance_state", None)

    val_json = df_to_dicts(pl.DataFrame(data), max_group_size=settings.max_json_group_size)
    if phase == ValidationPhase.SYNTACTICAL:
        single_errors = repo.get_field_counts(session, submission.id, Severity.ERROR, "single-field"),
        val_res = {
            "syntax_errors": {
                "single_field_count": single_errors,
                "multi_field_count": 0,  # this will always be zero for syntax errors
                "register_count": 0,  # this will always be zero for syntax errors
                "total_count": single_errors,
                "details": val_json,
            }
        }
    else:
        errors_list = [e for e in val_json if e["validation"]["severity"] == Severity.ERROR]
        warnings_list = [w for w in val_json if w["validation"]["severity"] == Severity.WARNING]
        val_res = {
            "syntax_errors": {
                "single_field_count": 0,
                "multi_field_count": 0,
                "register_count": 0,
                "total_count": 0,
                "details": [],
            },
            "logic_errors": {
                "single_field_count": repo.get_field_counts(session, submission.id, Severity.ERROR, "single-field"),
                "multi_field_count": repo.get_field_counts(session, submission.id, Severity.ERROR, "multi-field"),
                "register_count": repo.get_field_counts(session, submission.id, Severity.ERROR, "register"),
                "total_count": repo.get_field_counts(session, submission.id, Severity.ERROR),
                "details": errors_list,
            },
            "logic_warnings": {
                "single_field_count": repo.get_field_counts(session, submission.id, Severity.WARNING, "single-field"),
                "multi_field_count": repo.get_field_counts(session, submission.id, Severity.WARNING, "multi-field"),
                "register_count": 0,
                "total_count": repo.get_field_counts(session, submission.id, Severity.WARNING),
                "details": warnings_list,
            },
        }

    return val_res
"""
