# TODO: Fix Media Loading on Blackblaze B2

## Completed Tasks
- [x] Update settings.py to make media publicly accessible (AWS_DEFAULT_ACL = 'public-read', AWS_QUERYSTRING_AUTH = False)
- [x] Add URL logging to storage_backends.py for debugging
- [x] Modify storage_backends.py to check for B2 credentials and fallback to FileSystemStorage locally
- [x] Update settings.py to always use MediaStorage for DEFAULT_FILE_STORAGE

## Summary
Media files will now be uploaded to and served from Blackblaze B2 in production, but fallback to local FileSystemStorage in development if B2 credentials are not available, ensuring media loads in both environments.
