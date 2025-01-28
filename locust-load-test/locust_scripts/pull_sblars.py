import httpx
import os
import boto3
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig()

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

s3 = boto3.client('s3')

logging.getLogger('botocore.httpchecksum').setLevel(logging.WARNING)


def delete_files():
    sblar_dir = os.getenv("SBLAR_LOCATION", "./locust-load-test/sblars")
    for file in os.listdir(sblar_dir):
        file_path = os.path.join(sblar_dir, file)
        os.remove(file_path)


def download_file(client, file_url, local_path):
    response = client.get(file_url)
    response.raise_for_status()
    if not os.path.exists(local_path):
        with open(local_path, "wb") as file:
            file.write(response.content)


def pull_files(client, contents, url):
    sblar_dir = os.getenv("SBLAR_LOCATION", "./locust-load-test/sblars")
    for file in contents:
        if file["type"] == "file":
            local_path = os.path.join(sblar_dir, file["name"])
            if not os.path.exists(sblar_dir):
                os.makedirs(sblar_dir)
            if not os.path.exists(local_path):
                download_file(client, file["download_url"], local_path)
        elif file["type"] == "dir":
            response = client.get(url)
            response.raise_for_status()
            contents = response.json()
            folder_url = url + f"{file['name']}/"
            pull_files(client, contents, folder_url)


def download_files():
    log.info("downloading sblars")
    sblar_dir = os.getenv("SBLAR_LOCATION", "./locust-load-test/sblars")
    if not os.path.exists(sblar_dir):
        os.makedirs(sblar_dir)
    if os.getenv("TEST_FILE_LOCATION", "s3") == "s3":
        bucket = os.getenv("BUCKET", "")
        folder = os.getenv("FOLDER", "")
        response = s3.list_objects_v2(Bucket=bucket, Prefix=folder)
        for file in response.get("Contents", []):
            fname: str = file["Key"].split("/")[-1]
            if fname.endswith(".csv"):
                local_path = os.path.join(sblar_dir, fname)
                if not os.path.exists(local_path):
                    s3.download_file(bucket, file["Key"], local_path)
        log.info("sblars downloaded from s3")
    else:
        with httpx.Client() as client:
            url = os.getenv("SBLAR_REPO", "https://api.github.com/repos/cfpb/sbl-test-data/contents/locust-sblars")
            response = client.get(url)
            response.raise_for_status()
            contents = response.json()
            pull_files(client, contents, url)
        log.info("sblars downloaded from git")


download_files()