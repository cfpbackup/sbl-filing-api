import logging
import shutil
from typing import BinaryIO, Generator
import boto3
from pathlib import Path
from sbl_filing_api.config import FsProtocol, settings

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def upload(path: str, content: bytes) -> None:
    if settings.fs_upload_config.protocol == FsProtocol.FILE:
        file = Path(f"{settings.fs_upload_config.root}/{path}")
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(content)
    else:
        s3 = boto3.client("s3")
        r = s3.put_object(
            Bucket=settings.fs_upload_config.root,
            Key=path,
            Body=content,
        )
        log.debug(
            "s3 upload response for key: %s, period: %s file: %s, response: %s",
            path,
            r,
        )

def upload_file(path: str, content: BinaryIO) -> None:
    if settings.fs_upload_config.protocol == FsProtocol.FILE:
        log.info("local")
        file = Path(f"{settings.fs_upload_config.root}/{path}")
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open("wb") as f:
            shutil.copyfileobj(content, f)
            # f.write(content)
        # file.write_bytes(content)
    else:
        log.info("s3")
        s3 = boto3.client("s3")
        r = s3.upload_fileobj(
            Bucket=settings.fs_upload_config.root,
            Key=path,
            Fileobj=content,
        )
        # r = s3.put_object(
        #     Bucket=settings.fs_upload_config.root,
        #     Key=path,
        #     Body=content,
        # )
        log.debug(
            "s3 upload response for key: %s, period: %s file: %s, response: %s",
            path,
            r,
        )

def download(path: str) -> Generator:
    if settings.fs_upload_config.protocol == FsProtocol.FILE:
        with open(f"{settings.fs_upload_config.root}/{path}") as f:
            yield from f
    else:
        s3 = boto3.client("s3")
        r = s3.get_object(
            Bucket=settings.fs_upload_config.root,
            Key=path,
        )
        with r["Body"] as f:
            yield from f
