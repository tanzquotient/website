#!/usr/bin/env python3

import os
import json

from minio import Minio
from minio.error import MinioException

from dotenv import load_dotenv

load_dotenv()


# Initialize minioClient with an endpoint and access/secret keys.
endpoint = os.environ.get("TQ_S3_MEDIA_HOST") + ":" + os.environ.get("TQ_S3_MEDIA_PORT")
minio_client = Minio(
    endpoint,
    access_key=os.environ.get("TQ_S3_MEDIA_ACCESS_KEY"),
    secret_key=os.environ.get("TQ_S3_MEDIA_SECRET_KEY"),
    secure=False,
)

try:
    print("creating media bucket")
    minio_client.make_bucket(
        os.environ.get("TQ_S3_MEDIA_BUCKET"),
        location=os.environ.get("TQ_S3_MEDIA_REGION"),
    )
except MinioException:
    pass

try:
    print("creating static bucket")
    minio_client.make_bucket(
        os.environ.get("TQ_S3_STATIC_BUCKET"),
        location=os.environ.get("TQ_S3_STATIC_REGION"),
    )
except MinioException:
    pass

try:
    print("creating finance bucket")
    minio_client.make_bucket(
        os.environ.get("TQ_S3_FINANCE_BUCKET"),
        location=os.environ.get("TQ_S3_FINANCE_REGION"),
    )
except MinioException:
    pass

print("configure static bucket")
static_bucket = os.environ.get("TQ_S3_STATIC_BUCKET")
policy_static_read_only = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
            "Resource": "arn:aws:s3:::{}".format(static_bucket),
        },
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::{}/*".format(static_bucket),
        },
    ],
}
policy = minio_client.set_bucket_policy(
    static_bucket, json.dumps(policy_static_read_only)
)
