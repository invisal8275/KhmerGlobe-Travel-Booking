from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Inquiry, Review

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=80, required=True)
    last_name = forms.CharField(max_length=80, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["start_date", "end_date", "travelers", "payment_method", "notes"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us about preferences, pickup, room, or other details."}),
        }


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["name", "email", "inquiry_type", "details"]
        widgets = {"details": forms.Textarea(attrs={"rows": 5})}


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {"comment": forms.Textarea(attrs={"rows": 4})}


class PaymentReferenceForm(forms.ModelForm):
    class Meta:
        from .models import Payment
        model = Payment
        fields = ["transaction_reference"]
        widgets = {"transaction_reference": forms.TextInput(attrs={"placeholder": "Bank transfer reference / receipt number"})}
