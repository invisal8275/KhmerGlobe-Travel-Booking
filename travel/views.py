from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
import json
from html import escape
from pathlib import Path
from io import BytesIO
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import RegisterForm, BookingForm, InquiryForm, ReviewForm, PaymentReferenceForm
from .models import Destination, Tour, Hotel, Booking, Payment, Inquiry, Review


def home(request):
    destinations = Destination.objects.filter(is_active=True, is_featured=True)[:4]
    tours = Tour.objects.filter(is_active=True).select_related("destination")[:6]
    hotels = Hotel.objects.filter(is_active=True).select_related("destination")[:4]
    return render(request, "travel/home.html", {"destinations": destinations, "tours": tours, "hotels": hotels})


def tour_list(request):
    tours = Tour.objects.filter(is_active=True).select_related("destination")
    destination = request.GET.get("destination", "")
    query = request.GET.get("q", "").strip()
    tour_type = request.GET.get("type", "").strip()
    if destination:
        tours = tours.filter(destination__slug=destination)
    if query:
                tours = tours.filter(Q(title__icontains=query) | Q(destination__name__icontains=query))
    if tour_type:
        tours = tours.filter(tour_type=tour_type)
    return render(request, "travel/tours.html", {"tours": tours, "destinations": Destination.objects.filter(is_active=True)})


def tour_detail(request, slug):
    tour = get_object_or_404(Tour, slug=slug, is_active=True)
    return render(request, "travel/tour_detail.html", {"tour": tour})


def hotel_list(request):
    hotels = Hotel.objects.filter(is_active=True).select_related("destination")
    return render(request, "travel/hotels.html", {"hotels": hotels})


def hotel_detail(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, is_active=True)
    return render(request, "travel/hotel_detail.html", {"hotel": hotel})


def register(request):
    if request.user.is_authenticated:
        return redirect("customer_dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your KhmerGlobe account is ready.")
        return redirect("customer_dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def create_tour_booking(request, slug):
    tour = get_object_or_404(Tour, slug=slug, is_active=True)
    form = BookingForm(request.POST or None, initial={"travelers": 1, "start_date": date.today()})
    if request.method == "POST" and form.is_valid():
        booking = form.save(commit=False)
        booking.customer = request.user
        booking.tour = tour
        booking.hotel = None
        booking.total_amount = tour.price_per_person * booking.travelers
        booking.full_clean()
        booking.save()
        Payment.objects.create(booking=booking, amount=booking.total_amount, method=booking.get_payment_method_display())
        messages.success(request, f"Request {booking.reference} was submitted. The team will confirm availability.")
        return redirect("booking_detail", reference=booking.reference)
    return render(request, "travel/booking_form.html", {"form": form, "item": tour, "kind": "tour"})


@login_required
def create_hotel_booking(request, slug):
    hotel = get_object_or_404(Hotel, slug=slug, is_active=True)
    form = BookingForm(request.POST or None, initial={"travelers": 1, "start_date": date.today()})
    if request.method == "POST" and form.is_valid():
        if not form.cleaned_data.get("end_date") or form.cleaned_data["end_date"] <= form.cleaned_data["start_date"]:
            form.add_error("end_date", "Please choose a check-out date after check-in.")
            return render(request, "travel/booking_form.html", {"form": form, "item": hotel, "kind": "hotel"})
        booking = form.save(commit=False)
        booking.customer = request.user
        booking.hotel = hotel
        booking.tour = None
        booking.full_clean()
        booking.save()
        Payment.objects.create(booking=booking, amount=booking.total_amount, method=booking.get_payment_method_display())
        messages.success(request, f"Hotel request {booking.reference} was submitted for availability confirmation.")
        return redirect("booking_detail", reference=booking.reference)
    return render(request, "travel/booking_form.html", {"form": form, "item": hotel, "kind": "hotel"})


# Planning estimates for the trip builder. These are configurable sample rates,
# not live supplier quotations. Recalculate and confirm the final quote with staff.
TRANSPORT_OPTIONS = {
    "bus": {"label": "Shared / tourist bus", "basis": "per traveller per day", "rate": Decimal("18.00"), "capacity": 1},
    "tuk_tuk": {"label": "Tuk-tuk", "basis": "per vehicle per day", "rate": Decimal("22.00"), "capacity": 3},
    "motorbike": {"label": "Motorbike rental", "basis": "per bike per day", "rate": Decimal("16.00"), "capacity": 1},
    "private_car": {"label": "Private car with driver", "basis": "per vehicle per day", "rate": Decimal("65.00"), "capacity": 3},
    "van": {"label": "Private van with driver", "basis": "per vehicle per day", "rate": Decimal("90.00"), "capacity": 8},
    "boat": {"label": "Boat / ferry connection", "basis": "per traveller (one trip)", "rate": Decimal("28.00"), "capacity": 1},
    "flight_quote": {"label": "Domestic / regional flight", "basis": "price confirmed by our team", "rate": Decimal("0.00"), "capacity": 1},
}
ACTIVITY_OPTIONS = {
    "local_guide": {"label": "Private local guide", "rate": Decimal("45.00"), "basis": "per day"},
    "cooking_class": {"label": "Khmer cooking class", "rate": Decimal("25.00"), "basis": "per traveller"},
    "boat_excursion": {"label": "Local boat excursion", "rate": Decimal("30.00"), "basis": "per traveller"},
    "airport_transfer": {"label": "Airport pickup / drop-off", "rate": Decimal("18.00"), "basis": "per vehicle"},
}


def trip_builder(request):
    destinations = Destination.objects.filter(is_active=True).order_by("name")
    tours = Tour.objects.filter(is_active=True).select_related("destination").order_by("title")
    hotels = Hotel.objects.filter(is_active=True).select_related("destination").order_by("name")

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.info(request, "Please sign in or create an account before submitting your trip.")
            return redirect("login")

        errors = []
        try:
            destination_id = int(request.POST.get("destination_id", "0"))
            destination = Destination.objects.filter(pk=destination_id, is_active=True).first()
        except (ValueError, TypeError):
            destination = None
        if destination is None:
            errors.append("Choose a destination.")

        try:
            start_date = date.fromisoformat(request.POST.get("start_date", ""))
            if start_date < timezone.localdate():
                errors.append("Travel date cannot be in the past.")
        except (ValueError, TypeError):
            start_date = None
            errors.append("Choose a valid departure date.")

        try:
            days = int(request.POST.get("days", "1"))
            travelers = int(request.POST.get("travelers", "1"))
            rooms = int(request.POST.get("rooms", "1"))
            if not 1 <= days <= 30: errors.append("Trip duration must be between 1 and 30 days.")
            if not 1 <= travelers <= 50: errors.append("Travellers must be between 1 and 50.")
            if not 1 <= rooms <= 25: errors.append("Rooms must be between 1 and 25.")
        except (ValueError, TypeError):
            days, travelers, rooms = 1, 1, 1
            errors.append("Check the duration, traveller and room counts.")

        tour = None
        tour_id = request.POST.get("tour_id", "").strip()
        if tour_id:
            try:
                tour = Tour.objects.filter(pk=int(tour_id), is_active=True).select_related("destination").first()
            except (ValueError, TypeError):
                tour = None
            if not tour or not destination or tour.destination_id != destination.id:
                errors.append("The selected tour is not available for this destination.")
            elif days != tour.duration_days:
                errors.append(f"This tour package is {tour.duration_days} days. Please use its advertised duration.")

        hotel = None
        hotel_id = request.POST.get("hotel_id", "").strip()
        if hotel_id:
            try:
                hotel = Hotel.objects.filter(pk=int(hotel_id), is_active=True).select_related("destination").first()
            except (ValueError, TypeError):
                hotel = None
            if not hotel or not destination or hotel.destination_id != destination.id:
                errors.append("The selected hotel is not available for this destination.")

        transport_code = request.POST.get("transport", "bus")
        transport = TRANSPORT_OPTIONS.get(transport_code)
        if not transport:
            errors.append("Choose a valid transport option.")
            transport_code, transport = "bus", TRANSPORT_OPTIONS["bus"]

        payment_method = request.POST.get("payment_method", "")
        if payment_method not in ("visa_card", "khqr"):
            errors.append("Choose Visa / Mastercard or KHQR as your payment method.")

        activity_codes = request.POST.getlist("activities")
        invalid_activities = [code for code in activity_codes if code not in ACTIVITY_OPTIONS]
        if invalid_activities:
            errors.append("One or more selected activities are invalid.")

        if not errors and destination and start_date:
            end_date = start_date + timedelta(days=days)
            nights = max(days - 1, 0)
            tour_cost = (tour.price_per_person * travelers) if tour else Decimal("0.00")
            hotel_cost = (hotel.price_per_night * nights * rooms) if hotel and nights else Decimal("0.00")

            if transport_code in ("bus",):
                transport_units = travelers * days
            elif transport_code in ("tuk_tuk", "private_car", "van", "motorbike"):
                import math
                vehicles = math.ceil(travelers / transport["capacity"])
                transport_units = vehicles * days
            elif transport_code == "boat":
                transport_units = travelers
            else:
                transport_units = 0
            transport_cost = transport["rate"] * transport_units

            activity_costs = {}
            for code in activity_codes:
                option = ACTIVITY_OPTIONS[code]
                if code == "local_guide":
                    amount = option["rate"] * days
                elif code == "airport_transfer":
                    import math
                    amount = option["rate"] * math.ceil(travelers / 3)
                else:
                    amount = option["rate"] * travelers
                activity_costs[code] = amount

            activities_total = sum(activity_costs.values(), Decimal("0.00"))
            total = tour_cost + hotel_cost + transport_cost + activities_total

            snapshot = {
                "destination": destination.name,
                "country": destination.country,
                "tour": tour.title if tour else "Custom independent trip",
                "hotel": hotel.name if hotel else "No hotel selected",
                "hotel_category": hotel.category if hotel else None,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days,
                "nights": nights,
                "travelers": travelers,
                "rooms": rooms if hotel else 0,
                "transport": transport["label"],
                "transport_note": "Flight fare requires a separate quotation." if transport_code == "flight_quote" else transport["basis"],
                "activities": [{"name": ACTIVITY_OPTIONS[c]["label"], "amount": str(activity_costs[c])} for c in activity_codes],
                "breakdown": {
                    "tour": str(tour_cost), "hotel": str(hotel_cost),
                    "transport": str(transport_cost), "activities": str(activities_total),
                },
                "price_note": "Planning estimate in USD. Supplier availability, taxes, exact room rates and transport schedules must be confirmed before payment.",
            }
            booking = Booking(
                customer=request.user,
                tour=tour,
                hotel=hotel,
                start_date=start_date,
                end_date=end_date,
                travelers=travelers,
                total_amount=total,
                payment_method=payment_method,
                payment_status="pending",
                status="pending",
                notes=json.dumps(snapshot, ensure_ascii=False),
            )
            booking.save()
            Payment.objects.create(
                booking=booking,
                amount=total,
                method="Visa / Mastercard via ABA PayWay" if payment_method == "visa_card" else "KHQR via ABA PayWay",
                status="pending",
            )
            return redirect("trip_checkout", reference=booking.reference)

        for error in errors:
            messages.error(request, error)

    return render(request, "travel/trip_builder.html", {
        "destinations": destinations,
        "tours": tours,
        "hotels": hotels,
        "transport_options": TRANSPORT_OPTIONS,
        "activity_options": ACTIVITY_OPTIONS,
        "today": timezone.localdate().isoformat(),
    })


@login_required
def trip_checkout(request, reference):
    booking = get_object_or_404(Booking, reference=reference, customer=request.user)
    try:
        trip = json.loads(booking.notes or "{}")
    except (TypeError, json.JSONDecodeError):
        trip = {}
    payment = booking.payments.order_by("-created_at").first()

    if request.method == "POST":
        if booking.payment_status == "paid":
            messages.info(request, "This booking has already been paid.")
            return redirect("trip_checkout", reference=reference)
        transaction_reference = request.POST.get("transaction_reference", "").strip()
        receipt = request.FILES.get("receipt_file")
        errors = []
        if booking.payment_method not in ("khqr", "bank"):
            errors.append("Receipt upload is currently for KHQR payments. Visa checkout must use the secure payment gateway.")
        if not transaction_reference:
            errors.append("Enter the transaction/reference number shown by your banking app.")
        if not receipt:
            errors.append("Upload your payment receipt.")
        else:
            ext = Path(receipt.name).suffix.lower()
            if ext not in (".jpg", ".jpeg", ".png", ".pdf"):
                errors.append("Receipt must be JPG, PNG or PDF.")
            if receipt.size > 5 * 1024 * 1024:
                errors.append("Receipt file must be 5 MB or smaller.")
            if receipt.content_type not in ("image/jpeg", "image/png", "application/pdf"):
                errors.append("Unsupported receipt file type.")
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            if payment is None:
                payment = Payment(booking=booking, amount=booking.total_amount, method="KHQR - ACLEDA static QR")
            # Replace previous proof when a customer resubmits after rejection.
            if payment.receipt_path:
                try:
                    default_storage.delete(payment.receipt_path)
                except Exception:
                    pass
            saved_name = default_storage.save(
                f"payment_receipts/{booking.reference}/{Path(receipt.name).name}", receipt
            )
            lines = [line for line in (payment.admin_note or "").splitlines() if not line.startswith("receipt_file:")]
            lines.append(f"receipt_file:{saved_name}")
            payment.admin_note = "\n".join(lines)
            payment.transaction_reference = transaction_reference[:120]
            payment.amount = booking.total_amount
            payment.status = "submitted"
            payment.save()
            booking.payment_status = "pending"
            booking.save(update_fields=["payment_status"])
            messages.success(request, "Your receipt and payment reference were submitted. Staff will verify the payment.")
            return redirect("trip_checkout", reference=booking.reference)

    return render(request, "travel/trip_checkout.html", {
        "booking": booking, "trip": trip, "payment": payment,
    })


@login_required
def booking_invoice(request, reference):
    booking = get_object_or_404(
        Booking.objects.select_related("customer", "tour", "hotel"),
        reference=reference, customer=request.user
    )
    if booking.payment_status != "paid":
        return HttpResponseForbidden("The invoice is available after payment has been verified.")
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    except ImportError:
        return HttpResponse("PDF invoice requires ReportLab. Install dependencies with: pip install -r requirements.txt", status=503)

    try:
        trip = json.loads(booking.notes or "{}")
    except (TypeError, json.JSONDecodeError):
        trip = {}
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Brand", parent=styles["Title"], textColor=colors.HexColor("#12394e"), fontSize=22, leading=26))
    customer_name = escape(booking.customer.get_full_name() or booking.customer.username)
    customer_email = escape(booking.customer.email or "Not provided")
    destination_name = escape(str(trip.get("destination", "Custom trip")))
    destination_country = escape(str(trip.get("country", "")))
    story = [
        Paragraph("KHMERGLOBE ULTRA+", styles["Brand"]),
        Paragraph("PAID BOOKING INVOICE", styles["Heading2"]),
        Spacer(1, 8*mm),
        Paragraph(f"<b>Booking reference:</b> {escape(booking.reference)}", styles["BodyText"]),
        Paragraph(f"<b>Customer:</b> {customer_name}", styles["BodyText"]),
        Paragraph(f"<b>Email:</b> {customer_email}", styles["BodyText"]),
        Paragraph(f"<b>Destination:</b> {destination_name}, {destination_country}", styles["BodyText"]),
        Paragraph(f"<b>Travel dates:</b> {booking.start_date} to {booking.end_date or 'TBC'}", styles["BodyText"]),
        Paragraph(f"<b>Travellers:</b> {booking.travelers}", styles["BodyText"]),
        Spacer(1, 6*mm),
    ]
    rows = [["Description", "Amount (USD)"]]
    breakdown = trip.get("breakdown", {})
    for label, key in [("Tour package", "tour"), ("Hotel", "hotel"), ("Transportation", "transport"), ("Activities", "activities")]:
        rows.append([label, f"${Decimal(str(breakdown.get(key, '0'))):,.2f}"])
    rows.append(["FULL PAYMENT RECEIVED", f"${booking.total_amount:,.2f}"])
    table = Table(rows, colWidths=[110*mm, 55*mm], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#12394e")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#d7e2e8")),
        ("ALIGN",(1,1),(-1,-1),"RIGHT"),
        ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#e8f6f2")),
        ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
        ("PADDING",(0,0),(-1,-1),9),
    ]))
    story.extend([table, Spacer(1, 8*mm),
        Paragraph(f"<b>Payment method:</b> {booking.get_payment_method_display()}", styles["BodyText"]),
        Paragraph("<b>Payment status:</b> PAID / VERIFIED", styles["BodyText"]),
        Paragraph("Thank you for booking with KhmerGlobe. Please keep this invoice for your records.", styles["BodyText"])])
    doc.build(story)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="KhmerGlobe-Invoice-{booking.reference}.pdf"'
    return response


@login_required
def customer_dashboard(request):
    bookings = Booking.objects.filter(customer=request.user).select_related("tour", "hotel", "tour__destination", "hotel__destination")
    return render(request, "travel/customer_dashboard.html", {"bookings": bookings})


@login_required
def booking_detail(request, reference):
    booking = get_object_or_404(Booking.objects.select_related("tour", "hotel", "tour__destination", "hotel__destination"), reference=reference, customer=request.user)
    return render(request, "travel/booking_detail.html", {"booking": booking})


@login_required
def cancel_booking(request, reference):
    booking = get_object_or_404(Booking, reference=reference, customer=request.user)
    if request.method == "POST" and booking.status == "pending":
        booking.status = "cancelled"
        booking.save(update_fields=["status"])
        messages.info(request, "Your pending booking request was cancelled.")
    return redirect("booking_detail", reference=reference)


@login_required
def submit_payment_reference(request, reference):
    booking = get_object_or_404(Booking, reference=reference, customer=request.user)
    payment = booking.payments.order_by("-created_at").first()
    if payment is None:
        messages.error(request, "No payment record exists for this booking yet.")
        return redirect("booking_detail", reference=reference)
    form = PaymentReferenceForm(request.POST or None, instance=payment)
    if request.method == "POST" and form.is_valid():
        payment = form.save(commit=False)
        payment.status = "submitted"
        payment.save()
        booking.payment_status = "pending"
        booking.save(update_fields=["payment_status"])
        messages.success(request, "Payment reference submitted for staff verification.")
        return redirect("booking_detail", reference=reference)
    return render(request, "travel/payment_reference.html", {"form": form, "booking": booking})


@login_required
def submit_review(request, reference):
    booking = get_object_or_404(Booking, reference=reference, customer=request.user, status="completed")
    if hasattr(booking, "review"):
        messages.info(request, "You have already reviewed this booking.")
        return redirect("booking_detail", reference=reference)
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.customer = request.user
        review.booking = booking
        review.save()
        messages.success(request, "Thank you. Your review will appear after moderation.")
        return redirect("booking_detail", reference=reference)
    return render(request, "travel/review_form.html", {"form": form, "booking": booking})


def contact(request):
    form = InquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        inquiry = form.save(commit=False)
        if request.user.is_authenticated:
            inquiry.customer = request.user
        inquiry.save()
        messages.success(request, "Your inquiry was received. Our team will contact you.")
        return redirect("home")
    return render(request, "travel/contact.html", {"form": form})


@user_passes_test(lambda u: u.is_staff)
def staff_dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    paid = Booking.objects.filter(payment_status="paid")
    context = {
        "booking_count": Booking.objects.count(),
        "pending_count": Booking.objects.filter(status="pending").count(),
        "customer_count": User.objects.filter(is_staff=False).count(),
        "revenue": paid.aggregate(total=Sum("total_amount"))["total"] or 0,
        "daily_revenue": paid.filter(created_at__date=today).aggregate(total=Sum("total_amount"))["total"] or 0,
        "monthly_revenue": paid.filter(created_at__date__gte=month_start, created_at__date__lte=today).aggregate(total=Sum("total_amount"))["total"] or 0,
        "paid_count": paid.count(),
        "unpaid_count": Booking.objects.exclude(payment_status="paid").count(),
        "bookings": Booking.objects.select_related("customer", "tour", "hotel").all()[:30],
        "payments": Payment.objects.select_related("booking", "booking__customer").order_by("-created_at")[:40],
        "inquiries": Inquiry.objects.filter(is_resolved=False)[:10],
    }
    return render(request, "travel/staff_dashboard.html", context)


@user_passes_test(lambda u: u.is_staff)
def update_booking_status(request, reference):
    booking = get_object_or_404(Booking, reference=reference)
    if request.method == "POST":
        status = request.POST.get("status")
        allowed = dict(Booking.STATUS)
        if status in allowed:
            booking.status = status
            booking.save(update_fields=["status"])
            messages.success(request, f"{booking.reference} updated to {allowed[status]}.")
    return redirect("staff_dashboard")


@user_passes_test(lambda u: u.is_staff)
def update_payment_status(request, payment_id):
    payment = get_object_or_404(Payment.objects.select_related("booking", "booking__customer"), pk=payment_id)
    if request.method == "POST":
        status = request.POST.get("status")
        admin_note = request.POST.get("admin_note", "").strip()
        if status in ("verified", "rejected"):
            if status == "verified":
                # Staff verification is required for manual KHQR. Never accept missing proof or a mismatched amount.
                if not payment.receipt_path or not payment.transaction_reference:
                    messages.error(request, "A receipt and transaction reference are required before approval.")
                    return redirect("staff_dashboard")
                if payment.amount != payment.booking.total_amount:
                    messages.error(request, "Payment amount does not match the booking total. Payment was not approved.")
                    return redirect("staff_dashboard")
                was_verified = payment.status == "verified"
                payment.status = "verified"
                payment.admin_note = "\n".join(
                    [line for line in (payment.admin_note or "").splitlines() if not line.startswith("staff_note:")] +
                    ([f"staff_note:{admin_note}"] if admin_note else [])
                )
                payment.save(update_fields=["status", "admin_note"])
                payment.booking.payment_status = "paid"
                payment.booking.status = "confirmed"
                payment.booking.save(update_fields=["payment_status", "status"])
                if not was_verified and payment.booking.customer.email:
                    invoice_url = request.build_absolute_uri(
                        __import__("django.urls", fromlist=["reverse"]).reverse("booking_invoice", args=[payment.booking.reference])
                    )
                    send_mail(
                        subject=f"KhmerGlobe booking confirmed — {payment.booking.reference}",
                        message=(
                            f"Dear {payment.booking.customer.get_full_name() or payment.booking.customer.username},\n\n"
                            f"Your full payment of USD {payment.booking.total_amount:,.2f} has been verified.\n"
                            f"Your booking {payment.booking.reference} is confirmed.\n"
                            f"Download your invoice after signing in: {invoice_url}\n\n"
                            "Thank you for choosing KhmerGlobe."
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[payment.booking.customer.email],
                        fail_silently=True,
                    )
                messages.success(request, f"Payment for {payment.booking.reference} verified and booking confirmed.")
            else:
                payment.status = "rejected"
                payment.admin_note = "\n".join(
                    [line for line in (payment.admin_note or "").splitlines() if not line.startswith("staff_note:")] +
                    ([f"staff_note:{admin_note}"] if admin_note else [])
                )
                payment.save(update_fields=["status", "admin_note"])
                payment.booking.payment_status = "unpaid"
                payment.booking.status = "pending"
                payment.booking.save(update_fields=["payment_status", "status"])
                messages.warning(request, f"Payment for {payment.booking.reference} rejected. Customer must resubmit proof.")
    return redirect("staff_dashboard")

