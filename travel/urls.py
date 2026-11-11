from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("plan-your-trip/", views.trip_builder, name="trip_builder"),
    path("checkout/<str:reference>/", views.trip_checkout, name="trip_checkout"),
    path("account/booking/<str:reference>/invoice/", views.booking_invoice, name="booking_invoice"),
    path("tours/", views.tour_list, name="tour_list"),
    path("tours/<slug:slug>/", views.tour_detail, name="tour_detail"),
    path("hotels/", views.hotel_list, name="hotel_list"),
    path("hotels/<slug:slug>/", views.hotel_detail, name="hotel_detail"),
    path("book/tour/<slug:slug>/", views.create_tour_booking, name="book_tour"),
    path("book/hotel/<slug:slug>/", views.create_hotel_booking, name="book_hotel"),
    path("account/register/", views.register, name="register"),
    path("account/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("account/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("account/", views.customer_dashboard, name="customer_dashboard"),
    path("account/booking/<str:reference>/", views.booking_detail, name="booking_detail"),
    path("account/booking/<str:reference>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("account/booking/<str:reference>/review/", views.submit_review, name="submit_review"),
    path("account/booking/<str:reference>/payment-reference/", views.submit_payment_reference, name="submit_payment_reference"),
    path("contact/", views.contact, name="contact"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/booking/<str:reference>/status/", views.update_booking_status, name="update_booking_status"),
    path("staff/payment/<int:payment_id>/status/", views.update_payment_status, name="update_payment_status"),
]
