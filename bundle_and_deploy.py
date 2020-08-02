#!/usr/bin/env python
"""
Bundle and deploy the Lambda function
v2.1.0
"""
import argparse
import shutil
import sys
import boto3
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser()
parser.add_argument(
    "function", help="The name of the AWS Lambda function to update.")
args = parser.parse_args()


def publish_new_version(artifact, func_name):
    """
    Publishes new version of the AWS Lambda Function
    """
    try:
        session = boto3.Session(profile_name='perfect4alexa')
        client = session.client('lambda', region_name='us-east-1')
    except ClientError as err:
        print("Failed to create boto3 client.\n" + str(err))
        return False

    try:
        response = client.update_function_code(
            FunctionName=str(func_name),
            ZipFile=open(artifact, 'rb').read(),
            Publish=False
        )
        print(response)
        return response
    except ClientError as err:
        print("Failed to update function code.\n" + str(err))
        return False
    except IOError as err:
        print("Failed to access " + artifact + ".\n" + str(err))
        return False


def create_bundle():
    """ Create our deployment bundle """
    try:
        shutil.copytree("src", ".tmp_build", dirs_exist_ok=True)
        shutil.copytree("deps", ".tmp_build", dirs_exist_ok=True)
    except FileNotFoundError as err:
        print("""
        Error creating deployment bundle. 
        Make sure both a 'src' and 'deps' directory exist.
        """)
        print(str(err))
        return False

    shutil.make_archive("lambda_function", "zip", ".tmp_build")
    shutil.rmtree(".tmp_build")
    return True


def main():
    " Your favorite wrapper's favorite wrapper "
    print("Creating deployment package...")
    create_bundle()

    print("Starting deploy...")
    published_new_version = publish_new_version(
        "lambda_function.zip", str(args.function))

    if published_new_version:
        print("New version successfully published!")
        sys.exit(0)
    else:
        print("Failed to deploy!")
        sys.exit(1)


if __name__ == "__main__":
    main()
