# KhmerGlobe Ultra+ — Django Booking Platform

A full-stack starter platform based on the KhmerGlobe front-end and the R.T.R Travel Service reference structure. It is a separate Django project and does not modify the user's existing loan-system project or database.

## Included
- Customer registration, login, logout, and personal booking dashboard
- Tour and hotel catalogues managed through Django Admin
- Tour booking requests and hotel reservation requests
- Unique booking references, booking statuses, estimated totals, and payment tracking
- Customer cancellation of pending requests
- Staff dashboard for booking status updates and inquiry review
- Payment status review (staff can verify/reject payment records)
- Customer reviews for completed bookings, with admin moderation
- Flight, visa, group, and general inquiry form
- Responsive travel-agency UI and dark/light theme
- Demo data seed command

## Quick start (Windows PowerShell)
1. Extract the ZIP.
2. Open PowerShell in the extracted `KhmerGlobe_Platform` folder.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Create database tables:
   ```powershell
   python manage.py makemigrations travel
   python manage.py migrate
   ```
6. Add sample destinations, tours, and hotels:
   ```powershell
   python manage.py seed_demo
   ```
7. Create the administrator:
   ```powershell
   python manage.py createsuperuser
   ```
8. Start the website:
   ```powershell
   python manage.py runserver
   ```
9. Visit:
   - Website: http://127.0.0.1:8000/
   - Staff dashboard: http://127.0.0.1:8000/staff/
   - Django admin: http://127.0.0.1:8000/django-admin/

## PostgreSQL (optional)
The default local setup uses a new SQLite file `db.sqlite3`, so it cannot overwrite your existing loan database. To use PostgreSQL, install `psycopg[binary]`, create a separate database named `khmerglobe_db`, and set the variables in `.env.example` in your shell with `DB_ENGINE=postgres`.

## Configure contact links
Telegram is configured as `https://t.me/+85585293131` for +855 85 293 131, and Facebook is configured as `https://www.facebook.com/hanumantravelcambodia/`. Replace the remaining `YOUR_EMAIL@example.com` placeholder with your official business email before launch.

## Important limitations / production work still required
- Tour and hotel bookings are requests, not instant confirmations. Staff must verify actual availability.
- No airline, hotel inventory, visa-provider, or channel-manager API is connected.
- Payment records are tracking only. No card data is collected and no payment gateway is connected. Add a supported payment provider (such as a locally available bank/payment gateway) only after obtaining merchant credentials and completing provider integration.
- Email currently uses Django's console backend. Configure SMTP before production.
- Demo content and sample hotel listings/prices must be replaced with verified business information.
- Before public deployment, set a strong `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, correct `DJANGO_ALLOWED_HOSTS`, HTTPS, backups, monitoring, and production static-file hosting. Have the application security-reviewed.

## Data model
Destination → Tour / Hotel → Booking → Payment; User → Booking / Inquiry / Review.


## Your uploaded destination photos
Four user-provided photos are included in `static/travel/images/destinations/`:
- `hanoi.jpg` — Hanoi, Vietnam
- `koh_rong.jpg` — Koh Rong, Cambodia
- `luang_prabang.jpg` — Luang Prabang, Laos
- `phnom_penh.jpg` — Phnom Penh, Cambodia

After copying these updated files into your existing project, run:
```powershell
python manage.py seed_demo
```
This updates the four destination records with local image paths. The Phnom Penh image is also used as the homepage hero background. Your existing `db.sqlite3` is not included in this ZIP and should be kept.


## Contact links supplied by the business
- Telegram: +855 85 293 131 — https://t.me/+85585293131
- Facebook: https://www.facebook.com/hanumantravelcambodia/

## Headquarters map
The Google Maps short link supplied for the headquarters resolves to a pin labelled in Khmer as Samdech Hun Sen Phnom Penh Thmey High School, near 11.581311, 104.8584177. Confirm whether this is intentionally the office pin before the site labels it as the headquarters.


## Presentation-ready tour and hotel catalogue update
The seed command now loads four detailed sample tour packages with day-by-day itineraries, inclusions and exclusions, and seven hotel showcase listings (Cambodia, Singapore and Dubai). It also updates the Siem Reap destination with an Angkor Wat photograph and adds destination records for Singapore and Dubai.

After replacing the project files, run these commands in the activated virtual environment:
```powershell
python manage.py makemigrations travel
python manage.py migrate
python manage.py seed_demo
```
The new Tour itinerary/inclusions/exclusions fields and Hotel amenities/room details/official website fields require the migration step. Do not delete your `db.sqlite3`.

**Pricing disclaimer:** Hotel and tour prices are illustrative USD starting estimates for a presentation catalogue, not live supplier rates, contractual offers or confirmed availability. Obtain a date-specific supplier quotation before publishing a sale or confirming a booking. Hotel inclusions vary by room/rate plan; the final supplier confirmation controls.

**Image disclaimer:** Some featured property and destination images are externally hosted by publishers/hotel sites. Confirm image licensing/permission and use approved hotel media assets before commercial publication. User-supplied local destination photos are stored under `static/travel/images/destinations/`.


## Payment methods footer strip
The supplied payment-methods artwork is displayed immediately above the website footer. It is included at `static/travel/images/payments/payment-methods.png`. Displaying payment logos does not mean the website is connected to or authorized to process those payment methods; configure a supported payment gateway and merchant account before accepting payments.


Cambodian payment display options have also been added to the footer: KHQR (Bakong), ABA Pay and ACLEDA Bank. These are visual payment-method labels only; connect and verify the relevant merchant/payment provider arrangements before claiming that the website can accept payments through them.


The footer's Cambodian payment row now uses the exact user-supplied ABA Bank and KHQR logo artwork, plus the additional Cambodian bank logo artwork supplied in chat. The second supplied logo has not been assigned a bank name because its identity was not confirmed.


## Custom trip builder and checkout workflow
A new `/plan-your-trip/` wizard lets a signed-in customer choose:
- Destination, departure date, duration and number of travellers
- An optional curated tour package
- An optional listed hotel, room count and nights
- Bus, tuk-tuk, motorbike, private car, van, boat or flight quotation
- Optional guide, cooking class, boat excursion and airport transfer
- Visa/Mastercard or KHQR as the preferred checkout method

The browser displays a running estimate, and the Django view independently recalculates all amounts from server-side rates before creating a pending booking and payment record. The full selection and price breakdown are stored in the booking notes as a JSON snapshot. These are sample planning rates and must be reviewed/updated by the business before public launch.

### Online payment activation
The checkout currently records the customer's preferred payment method and displays the pending booking summary. It does **not** collect card numbers, display a fake QR, mark a booking as paid, or claim a payment succeeded. Real Visa/Mastercard and KHQR checkout should be connected through ABA PayWay's hosted eCommerce checkout. Official developer documentation says PayWay supports card payments and KHQR and requires a sandbox merchant ID/API key, transaction verification, and a secured callback. Obtain your own merchant sandbox credentials from ABA PayWay, then implement/test the purchase request, transaction check and signed callback for your merchant account before production.
- Developer docs: https://developer.payway.com.kh/
- eCommerce checkout guide: https://developer.payway.com.kh/folder-3158159

Do not put merchant secrets in source code or send them in chat. Store them in environment variables on the server. Use sandbox credentials and test payments first, then request production activation from ABA.


### Payment policy
KhmerGlobe requires full payment (100% of the booking total) at checkout. The current checkout records the full amount due as a pending payment; actual charging remains disabled until the ABA PayWay hosted checkout and verified callback are implemented and configured.


## Added customer payment and operations features
- KHQR customers can upload a JPG/PNG/PDF payment receipt (max 5 MB) and submit a bank transaction reference.
- Staff dashboard includes a payment verification queue with receipt links and approve/reject actions.
- Approving a full matching payment marks the booking paid and confirmed and triggers a confirmation email.
- Paid customers can download a PDF invoice with their booking reference and price breakdown.
- Customer dashboard displays full booking history and invoice/payment actions.
- Staff dashboard includes daily and monthly paid-booking value, all-time paid value, booking counts and customer counts.

No new database fields were added for receipt paths: they are recorded in the existing Payment.admin_note field. Install dependencies with `pip install -r requirements.txt`. Configure SMTP settings for real email delivery. Local receipt storage is intended for development/classroom use; production should use protected media storage.
