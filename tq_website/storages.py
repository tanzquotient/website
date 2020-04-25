from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class TqStorage(S3Boto3Storage):
    def __init__(self, bucket_name):
        config = dict()
        if settings.S3_CUSTOM_DOMAIN:
            config['custom_domain'] = settings.S3_CUSTOM_DOMAIN.format(bucket_name)
        else:
            config['endpoint_url'] = settings.S3_ENDPOINT_URL
        super().__init__(bucket=bucket_name, **config)


class MediaStorage(TqStorage):
    def __init__(self):
        super().__init__(bucket_name=settings.BUCKET_MEDIA)


class StaticStorage(TqStorage):
    def __init__(self):
        super().__init__(bucket_name=settings.BUCKET_STATIC)


class PostfinanceStorage(TqStorage):
    def __init__(self):
        super().__init__(bucket_name=settings.BUCKET_POSTFINANCE)

