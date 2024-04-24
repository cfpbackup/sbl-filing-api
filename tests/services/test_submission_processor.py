import asyncio
import json

import pytest

from http import HTTPStatus
from sbl_filing_api.services import submission_processor
from fastapi import HTTPException
from unittest.mock import Mock, ANY, AsyncMock
from pytest_mock import MockerFixture
from sbl_filing_api.config import FsProtocol, settings
from sbl_filing_api.entities.models.dao import SubmissionDAO, SubmissionState


class TestSubmissionProcessor:
    @pytest.fixture
    def mock_fs(self, mocker: MockerFixture) -> Mock:
        fs_mock_patch = mocker.patch("sbl_filing_api.services.submission_processor.AbstractFileSystem")
        return fs_mock_patch.return_value

    @pytest.fixture
    def mock_fs_func(self, mocker: MockerFixture, mock_fs: Mock) -> Mock:
        fs_func_mock = mocker.patch("sbl_filing_api.services.submission_processor.filesystem")
        fs_func_mock.return_value = mock_fs
        return fs_func_mock

    @pytest.fixture
    def mock_upload_file(self, mocker: MockerFixture) -> Mock:
        file_mock = mocker.patch("fastapi.UploadFile")
        return file_mock.return_value

    async def test_upload(self, mocker: MockerFixture, mock_fs_func: Mock, mock_fs: Mock):
        with mocker.mock_open(mock_fs.open):
            await submission_processor.upload_to_storage("test_period", "test", "test", b"test content local")
        mock_fs_func.assert_called()
        mock_fs.mkdirs.assert_called()
        mock_fs.open.assert_called_with("../upload/upload/test_period/test/test.csv", "wb")
        file_handle = mock_fs.open()
        file_handle.write.assert_called_with(b"test content local")

    async def test_read_from_storage(self, mocker: MockerFixture, mock_fs_func: Mock, mock_fs: Mock):
        await submission_processor.get_from_storage("2024", "1234567890", "1_report")
        mock_fs_func.assert_called_with(**settings.fs_download_config.__dict__)
        mock_fs.open.assert_called_with("../upload/upload/2024/1234567890/1_report.csv", "r")

    async def test_upload_s3_no_mkdir(self, mocker: MockerFixture, mock_fs_func: Mock, mock_fs: Mock):
        default_fs_proto = settings.fs_upload_config.protocol
        settings.fs_upload_config.protocol = FsProtocol.S3.value
        default_mkdir = settings.fs_upload_config.mkdir
        settings.fs_upload_config.mkdir = False

        with mocker.mock_open(mock_fs.open):
            await submission_processor.upload_to_storage("test_period", "test", "test", b"test content s3")
        mock_fs_func.assert_called()
        mock_fs.mkdirs.assert_not_called()
        mock_fs.open.assert_called_with("../upload/upload/test_period/test/test.csv", "wb")
        file_handle = mock_fs.open()
        file_handle.write.assert_called_with(b"test content s3")

        settings.fs_upload_config.protocol = default_fs_proto
        settings.fs_upload_config.mkdir = default_mkdir

    async def test_upload_failure(self, mocker: MockerFixture, mock_fs_func: Mock, mock_fs: Mock):
        log_mock = mocker.patch("sbl_filing_api.services.submission_processor.log")
        mock_fs.mkdirs.side_effect = IOError("test")
        with pytest.raises(Exception) as e:
            await submission_processor.upload_to_storage("test_period", "test", "test", b"test content")
        log_mock.error.assert_called_with("Failed to upload file", ANY, exc_info=True, stack_info=True)
        assert isinstance(e.value, HTTPException)

    async def test_read_failure(self, mocker: MockerFixture, mock_fs_func: Mock, mock_fs: Mock):
        log_mock = mocker.patch("sbl_filing_api.services.submission_processor.log")
        mock_fs.open.side_effect = IOError("test")
        with pytest.raises(Exception) as e:
            await submission_processor.get_from_storage("2024", "1234567890", "1_report")
        log_mock.error.assert_called_with(
            "Failed to read file ../upload/upload/2024/1234567890/1_report.csv:", ANY, exc_info=True, stack_info=True
        )
        assert isinstance(e.value, HTTPException)

    def test_validate_file_supported(self, mock_upload_file: Mock):
        mock_upload_file.filename = "test.csv"
        mock_upload_file.content_type = "text/csv"
        mock_upload_file.size = settings.submission_file_size - 1
        submission_processor.validate_file_processable(mock_upload_file)

    def test_file_not_supported_invalid_extension(self, mock_upload_file: Mock):
        mock_upload_file.filename = "test.txt"
        mock_upload_file.content_type = "text/csv"
        mock_upload_file.size = settings.submission_file_size - 1
        with pytest.raises(HTTPException) as e:
            submission_processor.validate_file_processable(mock_upload_file)
        assert e.value.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    def test_file_not_supported_invalid_content_type(self, mock_upload_file: Mock):
        mock_upload_file.filename = "test.csv"
        mock_upload_file.content_type = "text/plain"
        mock_upload_file.size = settings.submission_file_size - 1
        with pytest.raises(HTTPException) as e:
            submission_processor.validate_file_processable(mock_upload_file)
        assert e.value.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    def test_file_not_supported_file_size_too_large(self, mock_upload_file: Mock):
        mock_upload_file.filename = "test.csv"
        mock_upload_file.content_type = "text/csv"
        mock_upload_file.size = settings.submission_file_size + 1
        with pytest.raises(HTTPException) as e:
            submission_processor.validate_file_processable(mock_upload_file)
        assert e.value.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE

    async def test_validate_and_update_successful(
        self,
        mocker: MockerFixture,
        successful_submission_mock: Mock,
        validation_success_mock: Mock,
        df_to_download_mock: Mock,
    ):
        mock_sub = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.SUBMISSION_UPLOADED,
            filename="submission.csv",
        )
        file_mock = mocker.patch("sbl_filing_api.services.submission_processor.upload_to_storage")
        df_to_download_mock.return_value = ""

        await submission_processor.validate_and_update_submission("2024", "123456790", mock_sub, None)
        encoded_results = df_to_download_mock.return_value.encode("utf-8")
        assert file_mock.mock_calls[0].args == (
            "2024",
            "123456790",
            "1" + submission_processor.REPORT_QUALIFIER,
            encoded_results,
        )
        json_results = json.loads(successful_submission_mock.mock_calls[1].args[0].validation_json)
        assert successful_submission_mock.mock_calls[0].args[0].state == SubmissionState.VALIDATION_IN_PROGRESS
        assert successful_submission_mock.mock_calls[0].args[0].validation_ruleset_version == "0.1.0"
        assert successful_submission_mock.mock_calls[1].args[0].state == "VALIDATION_SUCCESSFUL"
        assert json_results["syntax_errors"]["count"] == 0
        assert json_results["logic_errors"]["count"] == 0
        assert json_results["logic_warnings"]["count"] == 0

    async def test_validate_and_update_logic_warnings(
        self,
        mocker: MockerFixture,
        warning_submission_mock: Mock,
        validation_logic_warnings_mock: Mock,
        df_to_download_mock: Mock,
    ):
        mock_sub = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.SUBMISSION_UPLOADED,
            filename="submission.csv",
        )
        file_mock = mocker.patch("sbl_filing_api.services.submission_processor.upload_to_storage")

        await submission_processor.validate_and_update_submission("2024", "123456790", mock_sub, None)
        encoded_results = df_to_download_mock.return_value.encode("utf-8")
        assert file_mock.mock_calls[0].args == (
            "2024",
            "123456790",
            "1" + submission_processor.REPORT_QUALIFIER,
            encoded_results,
        )
        json_results = json.loads(warning_submission_mock.mock_calls[1].args[0].validation_json)
        assert warning_submission_mock.mock_calls[0].args[0].state == SubmissionState.VALIDATION_IN_PROGRESS
        assert warning_submission_mock.mock_calls[0].args[0].validation_ruleset_version == "0.1.0"
        assert warning_submission_mock.mock_calls[1].args[0].state == "VALIDATION_WITH_WARNINGS"
        assert json_results["syntax_errors"]["count"] == 0
        assert json_results["logic_errors"]["count"] == 0
        assert json_results["logic_warnings"]["count"] > 0

    async def test_validate_and_update_syntax_errors(
        self,
        mocker: MockerFixture,
        error_submission_mock: Mock,
        validation_syntax_errors_mock: Mock,
        df_to_download_mock: Mock,
    ):
        mock_sub = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.SUBMISSION_UPLOADED,
            filename="submission.csv",
        )

        file_mock = mocker.patch("sbl_filing_api.services.submission_processor.upload_to_storage")

        await submission_processor.validate_and_update_submission("2024", "123456790", mock_sub, None)
        encoded_results = df_to_download_mock.return_value.encode("utf-8")
        assert file_mock.mock_calls[0].args == (
            "2024",
            "123456790",
            "1" + submission_processor.REPORT_QUALIFIER,
            encoded_results,
        )
        json_results = json.loads(error_submission_mock.mock_calls[1].args[0].validation_json)
        assert error_submission_mock.mock_calls[0].args[0].state == SubmissionState.VALIDATION_IN_PROGRESS
        assert error_submission_mock.mock_calls[0].args[0].validation_ruleset_version == "0.1.0"
        assert error_submission_mock.mock_calls[1].args[0].state == "VALIDATION_WITH_ERRORS"
        assert json_results["syntax_errors"]["count"] > 0

    async def test_validate_and_update_logic_errors(
        self,
        mocker: MockerFixture,
        error_submission_mock: Mock,
        validation_logic_errors_mock: Mock,
        df_to_download_mock: Mock,
    ):
        mock_sub = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.SUBMISSION_UPLOADED,
            filename="submission.csv",
        )

        file_mock = mocker.patch("sbl_filing_api.services.submission_processor.upload_to_storage")

        await submission_processor.validate_and_update_submission("2024", "123456790", mock_sub, None)
        encoded_results = df_to_download_mock.return_value.encode("utf-8")
        assert file_mock.mock_calls[0].args == (
            "2024",
            "123456790",
            "1" + submission_processor.REPORT_QUALIFIER,
            encoded_results,
        )
        json_results = json.loads(error_submission_mock.mock_calls[1].args[0].validation_json)
        assert error_submission_mock.mock_calls[0].args[0].state == SubmissionState.VALIDATION_IN_PROGRESS
        assert error_submission_mock.mock_calls[0].args[0].validation_ruleset_version == "0.1.0"
        assert error_submission_mock.mock_calls[1].args[0].state == "VALIDATION_WITH_ERRORS"
        assert json_results["syntax_errors"]["count"] == 0
        assert json_results["logic_errors"]["count"] > 0
        assert json_results["logic_warnings"]["count"] == 0

    async def test_validate_and_update_logic_warnings_and_errors(
        self,
        mocker: MockerFixture,
        error_submission_mock: Mock,
        validation_logic_warnings_and_errors_mock: Mock,
        df_to_download_mock: Mock,
    ):
        mock_sub = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.SUBMISSION_UPLOADED,
            filename="submission.csv",
        )

        file_mock = mocker.patch("sbl_filing_api.services.submission_processor.upload_to_storage")

        await submission_processor.validate_and_update_submission("2024", "123456790", mock_sub, None)
        encoded_results = df_to_download_mock.return_value.encode("utf-8")
        assert file_mock.mock_calls[0].args == (
            "2024",
            "123456790",
            "1" + submission_processor.REPORT_QUALIFIER,
            encoded_results,
        )
        json_results = json.loads(error_submission_mock.mock_calls[1].args[0].validation_json)
        assert error_submission_mock.mock_calls[0].args[0].state == SubmissionState.VALIDATION_IN_PROGRESS
        assert error_submission_mock.mock_calls[0].args[0].validation_ruleset_version == "0.1.0"
        assert error_submission_mock.mock_calls[1].args[0].state == "VALIDATION_WITH_ERRORS"
        assert json_results["syntax_errors"]["count"] == 0
        assert json_results["logic_errors"]["count"] > 0
        assert json_results["logic_warnings"]["count"] > 0

    async def test_validate_and_update_submission_malformed(
        self,
        mocker: MockerFixture,
    ):
        log_mock = mocker.patch("sbl_filing_api.services.submission_processor.log")

        mock_sub = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.SUBMISSION_UPLOADED,
            filename="submission.csv",
        )

        mock_update_submission = mocker.patch("sbl_filing_api.services.submission_processor.update_submission")
        mock_update_submission.return_value = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.SUBMISSION_UPLOAD_MALFORMED,
            filename="submission.csv",
        )

        mock_read_csv = mocker.patch("pandas.read_csv")
        mock_read_csv.side_effect = RuntimeError("File not in csv format")

        await submission_processor.validate_and_update_submission("2024", "123456790", mock_sub, None)

        mock_update_submission.assert_called()
        log_mock.error.assert_called_with("The file is malformed", ANY, exc_info=True, stack_info=True)
        assert mock_update_submission.mock_calls[0].args[0].state == SubmissionState.VALIDATION_IN_PROGRESS
        assert mock_update_submission.mock_calls[1].args[0].state == SubmissionState.SUBMISSION_UPLOAD_MALFORMED

        mock_read_csv.side_effect = None
        mock_validation = mocker.patch("sbl_filing_api.services.submission_processor.validate_phases")
        mock_validation.side_effect = RuntimeError("File can not be parsed by validator")

        await submission_processor.validate_and_update_submission("2024", "123456790", mock_sub, None)
        log_mock.error.assert_called_with("The file is malformed", ANY, exc_info=True, stack_info=True)
        assert mock_update_submission.mock_calls[0].args[0].state == SubmissionState.VALIDATION_IN_PROGRESS
        assert mock_update_submission.mock_calls[1].args[0].state == SubmissionState.SUBMISSION_UPLOAD_MALFORMED

    async def test_validate_exception(
        self,
        mocker: MockerFixture,
    ):
        log_mock = mocker.patch("sbl_filing_api.services.submission_processor.log")

        mock_sub = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.SUBMISSION_UPLOADED,
            filename="submission.csv",
        )

        mock_update_submission = mocker.patch("sbl_filing_api.services.submission_processor.update_submission")
        mock_update_submission.return_value = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.VALIDATION_IN_PROGRESS,
            filename="submission.csv",
        )

        mocker.patch("pandas.read_csv")

        mock_validation = mocker.patch("sbl_filing_api.services.submission_processor.validate_phases")
        mock_validation.side_effect = KeyError(
            "None of ['validation_id', 'record_no', 'field_name'] are in the columns"
        )

        await submission_processor.validate_and_update_submission("2024", "123456790", mock_sub, b"\x00\x00")

        assert mock_update_submission.mock_calls[1].args[0].state == SubmissionState.VALIDATION_ERROR
        assert log_mock.mock_calls[0].error.assert_called_with(
            "Validation for submission 1 did not complete due to an unexpected error.",
            mock_validation.side_effect,
            exc_info=True,
            stack_info=True,
        )

    @pytest.mark.asyncio
    async def test_validation_monitor(
        self,
        mocker: MockerFixture,
    ):
        mock_sub = SubmissionDAO(
            id=1,
            filing=1,
            state=SubmissionState.SUBMISSION_UPLOADED,
            filename="submission.csv",
        )

        async def mock_validate_and_update_submission(
            period_code: str, lei: str, submission: SubmissionDAO, content: bytes
        ):
            await asyncio.sleep(5)
            return

        update_sub_patch = mocker.patch("sbl_filing_api.services.submission_processor.update_submission")
        mocker.patch("sbl_filing_api.services.submission_processor.settings.expired_submission_check_secs", 4)
        log_patch = mocker.patch("sbl_filing_api.services.submission_processor.log")

        validate_patch = mocker.patch(
            "sbl_filing_api.services.submission_processor.validate_and_update_submission", new_callable=AsyncMock
        )
        validate_patch.side_effect = mock_validate_and_update_submission

        await submission_processor.validation_monitor("2024", "1234TESTLEI000000001", mock_sub, b"\x00\x00")

        assert update_sub_patch.mock_calls[0].args[0].state == SubmissionState.VALIDATION_EXPIRED
        assert log_patch.mock_calls[0].warn.assert_called_with(
            "Validation for submission 1 did not complete within the expected timeframe, will be set to VALIDATION_EXPIRED.",
            ANY,
            exc_info=True,
            stack_info=True,
        )
