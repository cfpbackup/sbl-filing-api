from pytest_mock import MockerFixture
from unittest.mock import Mock
import io

from sbl_filing_api.config import FsProtocol, settings
import sbl_filing_api.services.file_handler as fh


def test_upload_local_fs(mocker: MockerFixture):
    default_file_proto = settings.fs_upload_config.protocol
    settings.fs_upload_config.protocol = FsProtocol.FILE

    path_mock = mocker.patch("sbl_filing_api.services.file_handler.Path")
    file_mock = Mock()
    path_mock.return_value = file_mock

    path = "test"
    content = b"test"
    fh.upload(path, b"test")
    path_mock.assert_called_with(f"{settings.fs_upload_config.root}/{path}")
    file_mock.parent.mkdir.assert_called_with(parents=True, exist_ok=True)
    file_mock.write_bytes.assert_called_with(content)
    settings.fs_upload_config.protocol = default_file_proto


def test_upload_s3(mocker: MockerFixture):
    default_file_proto = settings.fs_upload_config.protocol
    settings.fs_upload_config.protocol = FsProtocol.S3

    boto3_mock = mocker.patch("sbl_filing_api.services.file_handler.boto3")
    client_mock = Mock()
    boto3_mock.client.return_value = client_mock

    path = "test"
    content = b"test"
    fh.upload(path, b"test")

    boto3_mock.client.assert_called_once_with("s3")
    client_mock.put_object.assert_called_once_with(
        Bucket=settings.fs_upload_config.root,
        Key=path,
        Body=content,
    )

    settings.fs_upload_config.protocol = default_file_proto


def test_download_local(mocker: MockerFixture):
    default_file_proto = settings.fs_upload_config.protocol
    settings.fs_upload_config.protocol = FsProtocol.FILE
    path = "test"
    content = "test content"
    open_mock = mocker.patch("builtins.open")
    res = ""
    with mocker.mock_open(open_mock, read_data=content):
        for chunk in fh.download(path):
            res += chunk
    open_mock.assert_called_once_with(f"{settings.fs_upload_config.root}/{path}")
    assert res == content
    settings.fs_upload_config.protocol = default_file_proto


def test_download_s3(mocker: MockerFixture):
    default_file_proto = settings.fs_upload_config.protocol
    settings.fs_upload_config.protocol = FsProtocol.S3
    path = "test"
    content = "test content"
    boto3_mock = mocker.patch("sbl_filing_api.services.file_handler.boto3")
    client_mock = Mock()
    boto3_mock.client.return_value = client_mock
    client_mock.get_object.return_value = {"Body": io.StringIO(content)}

    res = ""
    for chunk in fh.download(path):
        res += chunk

    boto3_mock.client.assert_called_once_with("s3")
    client_mock.get_object.assert_called_once_with(
        Bucket=settings.fs_upload_config.root,
        Key=path,
    )
    assert res == content
    settings.fs_upload_config.protocol = default_file_proto
