# Deploy KhmerGlobe on Render

## Before pushing
1. Run locally from the folder containing `manage.py`:
   `python manage.py makemigrations travel`
2. Confirm migration files were created under `travel/migrations/` (keep `__init__.py`).
3. Run `python manage.py migrate` and `python manage.py check`.
4. Commit and push the migration files and the Render deployment files:
   `git add .`
   `git commit -m "Prepare KhmerGlobe for Render deployment"`
   `git push`

Do not run `makemigrations` on Render. Migration files belong in Git.

## Deploy
1. Sign in at https://dashboard.render.com/ and connect GitHub account `invisal8275`.
2. Choose **New +** -> **Blueprint**.
3. Select repository `KhmerGlobe-Travel-Booking` and branch `main`.
4. Render reads `render.yaml` and proposes the web service and PostgreSQL database. Review the plan and any costs/expiry terms shown in the dashboard before confirming.
5. Wait for the build and deploy logs to finish. The build script installs requirements, collects static files and applies committed migrations.
6. Open the service URL ending in `.onrender.com`.
7. In the Render service Shell, run:
   `python manage.py createsuperuser`
8. Load catalogue records using:
   `python manage.py seed_demo`
   only if that command exists in the pushed repository and you want its sample catalogue.

## Important production limitations
- This Blueprint uses free Render plans for a classroom/demo deployment. Free web services can sleep when idle; check current Render plan limits. Free database plans may have limited lifetime/backup guarantees. Do not use this setup as the live production system for real customer bookings without reviewing paid database and service options.
- Uploaded KHQR receipts are currently stored on the app filesystem. Render's filesystem is ephemeral unless you configure persistent or external object storage. Do not accept real customer receipts until protected persistent media storage is configured.
- The static ACLEDA QR is not a dynamic payment integration. KHQR receipt review is manual. Visa/Mastercard are not activated until ABA PayWay is integrated and verified.
- Set real SMTP variables in Render Environment to send customer confirmation emails.
- Never upload `.env`, `db.sqlite3`, customer media/receipts, API secrets or passwords to GitHub.
