from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class TqStorage(S3Boto3Storage):

    def __init__(self, bucket_name, host, port, use_ssl, access_key, secret_key):
        config = dict(
            use_ssl=use_ssl,
            access_key=access_key,
            secret_key=secret_key,
        )
        if settings.S3_CUSTOM_DOMAIN:
            config['custom_domain'] = settings.S3_CUSTOM_DOMAIN.format(bucket_name)
        else:
            protocol = 'https' if use_ssl else 'http'
            config['endpoint_url'] = "{}://{}:{}".format(protocol, host, port)
        super().__init__(bucket=bucket_name, **config)


class MediaStorage(TqStorage):
    def __init__(self):
        super().__init__(
            bucket_name=settings.S3_MEDIA_BUCKET,
            host=settings.S3_MEDIA_HOST,
            port=settings.S3_MEDIA_PORT,
            use_ssl=settings.S3_MEDIA_USE_SSL,
            access_key=settings.S3_MEDIA_ACCESS_KEY,
            secret_key=settings.S3_MEDIA_SECRET_KEY,
        )


class StaticStorage(TqStorage):
    def __init__(self):
        super().__init__(
            bucket_name=settings.S3_STATIC_BUCKET,
            host=settings.S3_STATIC_HOST,
            port=settings.S3_STATIC_PORT,
            use_ssl=settings.S3_STATIC_USE_SSL,
            access_key=settings.S3_STATIC_ACCESS_KEY,
            secret_key=settings.S3_STATIC_SECRET_KEY,
        )


class PostfinanceStorage(TqStorage):
    def __init__(self):
        super().__init__(
            bucket_name=settings.S3_POSTFINANCE_BUCKET,
            host=settings.S3_POSTFINANCE_HOST,
            port=settings.S3_POSTFINANCE_PORT,
            use_ssl=settings.S3_POSTFINANCE_USE_SSL,
            access_key=settings.S3_POSTFINANCE_ACCESS_KEY,
            secret_key=settings.S3_POSTFINANCE_SECRET_KEY,
        )
