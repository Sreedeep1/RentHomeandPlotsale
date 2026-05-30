from django import forms
from .models import tbl_login
import re

class RegistrationForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        max_length=25,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    confirm_password = forms.CharField(
        max_length=25,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    phone = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # 🔹 Name validation (only alphabets & space)
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not re.match(r'^[A-Za-z\s]+$', name):
            raise forms.ValidationError("Name should contain only alphabets and spaces")
        return name

    # 🔹 Phone validation (10 digits only)
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\d{10}$', phone):
            raise forms.ValidationError("Phone number must be exactly 10 digits")
        return phone

    # 🔹 Email should not repeat
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if tbl_login.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email

    # 🔹 Password match validation
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")