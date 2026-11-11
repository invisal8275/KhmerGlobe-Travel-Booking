# KhmerGlobe online payment activation

The trip builder and checkout currently save the customer's payment preference as `visa_card` or `khqr` and create a pending payment record. They do not charge a card or generate a dynamic KHQR yet.

## Recommended gateway: ABA PayWay

ABA PayWay's official eCommerce checkout supports card payments and KHQR. It requires a PayWay sandbox merchant ID and API key, a server-generated signed purchase request, transaction-status verification, and a secured callback endpoint.

1. Register for an ABA PayWay sandbox merchant account: https://sandbox.payway.com.kh/
2. Review the official developer guide: https://developer.payway.com.kh/folder-3158159
3. Request production merchant onboarding from ABA after sandbox tests pass.
4. Copy `.env.example` to `.env` in your local environment and fill credentials from ABA. Keep `.env` private and never upload it or paste secret values into chat.
5. Complete the purchase request, callback signature verification, and check-transaction API for your merchant profile before accepting live money.

The payment UI intentionally does not ask customers to type card numbers into KhmerGlobe. Card entry should happen only in the provider's hosted/secure checkout. A booking stays pending until the provider confirms the transaction as paid.

## Trip calculator pricing

The transport and activity prices in `travel/views.py` are editable planning estimates. Update them to your actual supplier costs and business margins. Tour and hotel prices are read from the Django database. The server recalculates all submitted choices and does not trust the browser's displayed total.

## Apply this update

No database schema migration is required for this trip builder version. It reuses the existing Booking and Payment tables.

1. Back up your existing `db.sqlite3`.
2. Copy the updated project files over the current project, keeping your database.
3. Activate your virtual environment.
4. Run `python manage.py check`.
5. Run `python manage.py runserver`.
6. Sign in and open `/plan-your-trip/`.


## Payment amount policy
The booking flow is configured for **100% full payment at checkout**. No deposit or instalment option is offered. The amount sent to the payment provider must equal the server-calculated `Booking.total_amount`; mark the booking paid only after the provider's verified transaction status confirms the full amount and currency.


## Static ACLEDA KHQR display (manual verification)
The supplied ACLEDA KHQR image is displayed in a modal automatically when a customer reaches checkout with KHQR selected. Customers can scan it with ABA Mobile, ACLEDA mobile banking, or another app that supports KHQR. The checkout displays the booking's full amount separately because this uploaded QR is a static code and does not dynamically encode each booking amount/reference. Customers submit their bank transaction reference; staff must verify the actual incoming payment in the bank account before marking the booking paid. This is not automatic payment verification and is not a dynamic QR integration.


## Customer receipts, staff verification, email and invoices
- KHQR checkout requires the customer to enter the bank transaction reference and upload a JPG, PNG or PDF receipt (maximum 5 MB).
- Receipt files are saved under `MEDIA_ROOT/payment_receipts/`; the relative path is stored in the existing `Payment.admin_note` field, so this update does not add a database column or require a migration.
- Staff open `/staff/`, inspect the submitted receipt and independently check the bank account. Approve only when the incoming funds match the booking's full amount. Approval sets payment to verified/paid and booking to confirmed; rejection returns it to unpaid/pending.
- When a payment is newly verified, KhmerGlobe sends a confirmation email to the customer's account email. The default development email backend prints messages to the terminal. Configure SMTP environment variables for real email delivery.
- Paid customers can download a PDF invoice from their booking history or booking detail page. Install ReportLab via `pip install -r requirements.txt`.
- The customer account page is the booking history page. Staff revenue cards show the value of currently paid bookings created today and during the current month, plus all-time paid value and booking/customer counts.

## Media upload deployment
For local development, Django serves uploaded receipts from `/media/`. For production, configure a private or access-controlled media storage service and do not expose sensitive receipts publicly. The current simple local MEDIA_ROOT setup is suitable for a classroom/local demo only. Consider adding virus scanning and stricter file-content inspection before production.


## Apply the new receipt / invoice / admin dashboard update
This feature update reuses the existing database columns and does not require a schema migration.
1. Back up `db.sqlite3`.
2. Copy the updated ZIP contents over the project folder, preserving your local `.env` and database.
3. Activate the virtual environment in PowerShell.
4. Run `pip install -r requirements.txt` (adds ReportLab for PDF invoices).
5. Run `python manage.py check`.
6. Run `python manage.py runserver`.
7. Sign in as a staff/superuser and open `/staff/` to review submitted payment receipts.
8. Customers sign in and open `/account/` for booking history and paid invoices.

For actual confirmation emails, configure SMTP variables in your private `.env` file. During local development, the console email backend prints email content in the terminal. Local uploaded receipt files are served from `/media/` only with Django DEBUG enabled.
