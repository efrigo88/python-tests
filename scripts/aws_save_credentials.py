from pathlib import Path
import boto3
import os

PROFILES_NAMES = ["data-dev", "data-prod", "data-maintainer-prod"]
AWS_CREDENTIALS_PATH = Path(__file__).parent.absolute() / ".aws" / "credentials"


def profile_credentials(profile_name):
    session = boto3.Session(profile_name=profile_name, region_name="eu-west-1")
    credentials = session.get_credentials()

    credentials = credentials.get_frozen_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    token = credentials.token

    return access_key, secret_key, token


def get_file_content(profiles_names):
    cred_file_cont = ""

    for profile_name in profiles_names:
        access_key, secret_key, token = profile_credentials(profile_name)

        cred_file_cont = (
            cred_file_cont
            + f"""[{profile_name}]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
aws_session_token = {token}
region=eu-west-1

"""
        )
    return cred_file_cont


def write_credentials_file(file_content, credentials_file):
    f = open(credentials_file, "w+")
    f.write(file_content)
    f.close()


if __name__ == "__main__":
    try:
        os.remove(AWS_CREDENTIALS_PATH)
    except:
        pass

    credentials_cont = get_file_content(PROFILES_NAMES)
    write_credentials_file(credentials_cont, AWS_CREDENTIALS_PATH)
    print("Credentials updated successfully :)")
