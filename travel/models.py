import uuid
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

class Destination(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    country = models.CharField(max_length=100, default="Cambodia")
    summary = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.country}"


class Tour(models.Model):
    TOUR_TYPES = [("basic", "Basic tour"), ("incentive", "Incentive / Company"), ("vvip", "VVIP"), ("private", "Private tour"), ("group", "Group tour")]
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT, related_name="tours")
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    tour_type = models.CharField(max_length=20, choices=TOUR_TYPES, default="basic")
    duration_days = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(90)])
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(0)])
    summary = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    itinerary = models.TextField(blank=True, help_text="Day-by-day itinerary. Use one day per paragraph.")
    inclusions = models.TextField(blank=True, help_text="What is included in the package.")
    exclusions = models.TextField(blank=True, help_text="What is not included in the package.")
    image_url = models.CharField(max_length=500, blank=True)
    max_group_size = models.PositiveSmallIntegerField(default=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Hotel(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT, related_name="hotels")
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    summary = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    amenities = models.TextField(blank=True, help_text="One amenity per line.")
    room_details = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)
    website_url = models.URLField(blank=True)
    price_note = models.CharField(max_length=240, default="Indicative starting rate only; confirm live availability and taxes.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS = [("pending", "Pending review"), ("confirmed", "Confirmed"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    PAYMENT_STATUS = [("unpaid", "Unpaid"), ("pending", "Payment pending"), ("paid", "Paid"), ("refunded", "Refunded")]
    PAYMENT_METHODS = [("visa_card", "Visa / Mastercard card"), ("khqr", "KHQR QR payment"), ("bank", "Bank transfer"), ("cash", "Pay at office / on arrival"), ("other", "Discuss with our team")]
    reference = models.CharField(max_length=14, unique=True, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="travel_bookings")
    tour = models.ForeignKey(Tour, null=True, blank=True, on_delete=models.PROTECT, related_name="bookings")
    hotel = models.ForeignKey(Hotel, null=True, blank=True, on_delete=models.PROTECT, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    travelers = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(50)])
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    payment_method = models.CharField(max_length=12, choices=PAYMENT_METHODS, default="bank")
    payment_status = models.CharField(max_length=12, choices=PAYMENT_STATUS, default="unpaid")
    status = models.CharField(max_length=12, choices=STATUS, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = "KG" + uuid.uuid4().hex[:10].upper()
        if self.tour and not self.total_amount:
            self.total_amount = self.tour.price_per_person * self.travelers
        elif self.hotel and not self.total_amount and self.end_date:
            nights = max((self.end_date - self.start_date).days, 1)
            self.total_amount = self.hotel.price_per_night * nights
        super().save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be after start date."})

    def __str__(self):
        return f"{self.reference} — {self.customer}"


class Payment(models.Model):
    STATUS = [("pending", "Pending"), ("submitted", "Proof submitted"), ("verified", "Verified"), ("rejected", "Rejected")]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30, default="bank transfer")
    transaction_reference = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="pending")
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def receipt_path(self):
        for line in (self.admin_note or "").splitlines():
            if line.startswith("receipt_file:"):
                return line.split(":", 1)[1].strip()
        return ""

    @property
    def receipt_url(self):
        if not self.receipt_path:
            return ""
        from django.core.files.storage import default_storage
        return default_storage.url(self.receipt_path)

    def __str__(self):
        return f"{self.booking.reference} — {self.amount} USD"


class Inquiry(models.Model):
    TYPES = [("flight", "Flight"), ("visa", "Visa"), ("general", "General"), ("group", "Group / MICE")]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    inquiry_type = models.CharField(max_length=12, choices=TYPES, default="general")
    details = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Review(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="review")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
