from b2sdk.v2 import B2Api, InMemoryAccountInfo

def get_signed_url(bucket_name: str, filename: str, duration: int = 3600):
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", "YOUR_KEY_ID", "YOUR_APP_KEY")

    bucket = b2_api.get_bucket_by_name(bucket_name)
    auth_token = bucket.get_download_authorization(
        file_name_prefix=filename,
        valid_duration_in_seconds=duration
    )

    return f"https://f005.backblazeb2.com/file/{bucket_name}/{filename}?Authorization={auth_token}"
