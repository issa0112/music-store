# TODO: Fix OperationalError: no such table: store_artist

## Issue
The error "OperationalError: no such table: store_artist" occurs in production on Render because the database tables are missing. This is due to DEBUG being True in production (since DJANGO_ENV is not set to "production"), causing the app to use SQLite instead of the configured PostgreSQL database. SQLite on Render is not persistent and resets on each deploy.

## Solution Steps
- [ ] Set environment variable DJANGO_ENV=production in Render's dashboard to ensure production settings are used.
- [ ] Set environment variable DATABASE_URL=postgres://musicstoredb_user:R6Fg89113RMTqtVSUZgnT526ETASsQf3@dpg-d4u6rcfgi27c738fj640-a:5432/musicstoredb in Render's environment variables.
- [ ] Redeploy the app on Render to apply migrations and create the database tables.

## Completed Tasks
- [x] Update settings.py to make media publicly accessible (AWS_DEFAULT_ACL = 'public-read', AWS_QUERYSTRING_AUTH = False)
- [x] Add URL logging to storage_backends.py for debugging
- [x] Modify storage_backends.py to check for B2 credentials and fallback to FileSystemStorage locally
- [x] Update settings.py to always use MediaStorage for DEFAULT_FILE_STORAGE

## Summary
After setting the environment variables and redeploying, the app will use the persistent PostgreSQL database, and migrations will be applied during the build process, resolving the table error. Media files will continue to be uploaded to and served from Blackblaze B2 in production, with fallback to local FileSystemStorage in development.
