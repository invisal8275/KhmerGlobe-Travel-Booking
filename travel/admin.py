from django.contrib import admin
from .models import Destination, Tour, Hotel, Booking, Payment, Inquiry, Review

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "is_featured", "is_active")
    list_filter = ("country", "is_featured", "is_active")
    search_fields = ("name", "country")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("title", "destination", "tour_type", "duration_days", "price_per_person", "is_active")
    list_filter = ("tour_type", "destination", "is_active")
    search_fields = ("title", "destination__name")
    fields = ("destination", "title", "slug", "tour_type", "duration_days", "price_per_person", "summary", "description", "itinerary", "inclusions", "exclusions", "image_url", "max_group_size", "is_active")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "destination", "category", "price_per_night", "is_active")
    list_filter = ("category", "destination", "is_active")
    search_fields = ("name", "destination__name")
    fields = ("destination", "name", "slug", "category", "price_per_night", "summary", "description", "amenities", "room_details", "image_url", "website_url", "price_note", "is_active")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer", "tour", "hotel", "start_date", "status", "payment_status", "total_amount")
    list_filter = ("status", "payment_status", "payment_method")
    search_fields = ("reference", "customer__username", "customer__email")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "method", "status", "created_at", "receipt_link")
    list_filter = ("status", "method")
    readonly_fields = ("receipt_link",)

    @admin.display(description="Uploaded receipt")
    def receipt_link(self, obj):
        from django.utils.html import format_html
        return format_html('<a href="{}" target="_blank" rel="noopener">Open receipt</a>', obj.receipt_url) if obj.receipt_url else "No receipt"

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "inquiry_type", "is_resolved", "created_at")
    list_filter = ("inquiry_type", "is_resolved")
    search_fields = ("name", "email", "details")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("customer", "booking", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved")
