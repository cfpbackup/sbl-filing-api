from enum import Enum


class SubmissionState(str, Enum):
    SUBMISSION_UPLOADED = "SUBMISSION_UPLOADED"
    VALIDATION_IN_PROGRESS = "VALIDATION_IN_PROGRESS"
    VALIDATION_WITH_ERRORS = "VALIDATION_WITH_ERRORS"
    VALIDATION_WITH_WARNINGS = "VALIDATION_WITH_WARNINGS"
    VALIDATION_SUCCESSFUL = "VALIDATION_SUCCESSFUL"
    SUBMISSION_CERTIFIED = "SUBMISSION_CERTIFIED"


class FilingTaskState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class FilingType(str, Enum):
    ANNUAL = "ANNUAL"
