import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import TouristProfile

class TouristRegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name',
            'id': 'reg_full_name'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a unique username',
            'autocomplete': 'username',
            'id': 'reg_username'
        })
    )
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'autocomplete': 'email',
            'id': 'reg_email'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. +91 9876543210',
            'autocomplete': 'tel',
            'id': 'reg_phone'
        })
    )
    password = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a secure password',
            'autocomplete': 'new-password',
            'id': 'reg_password'
        })
    )
    confirm_password = forms.CharField(
        required=True,
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
            'id': 'reg_confirm_password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("Username may only contain letters, numbers, and @/./+/-/_ characters.")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        # Clean phone check: allow digits, spaces, hyphens, and leading +
        digits = re.sub(r'[^\d]', '', phone)
        if len(digits) < 10 or len(digits) > 15:
            raise ValidationError("Please provide a valid phone number (10 to 15 digits).")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match. Please re-enter.")
            else:
                # Apply Django password validators
                temp_user = User(
                    username=cleaned_data.get('username', ''),
                    email=cleaned_data.get('email', '')
                )
                try:
                    validate_password(password, user=temp_user)
                except ValidationError as e:
                    self.add_error('password', e)

        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        full_name = cleaned_data['full_name'].strip()
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        # Explicitly ensure NO staff or superuser privileges can ever be granted
        user = User(
            username=cleaned_data['username'],
            email=cleaned_data['email'],
            first_name=first_name,
            last_name=last_name,
            is_staff=False,
            is_superuser=False,
            is_active=True
        )
        user.set_password(cleaned_data['password'])
        user.save()

        # Create TouristProfile linked to user
        profile = TouristProfile.objects.create(
            user=user,
            phone_number=cleaned_data['phone_number']
        )
        return user


class TouristLoginForm(forms.Form):
    username_or_email = forms.CharField(
        max_length=150,
        required=True,
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email',
            'autocomplete': 'username',
            'id': 'login_username_or_email'
        })
    )
    password = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
            'id': 'login_password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label="Remember me",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'remember_me'
        })
    )


class TouristProfileEditForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'id': 'profile_first_name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Last Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'id': 'profile_last_name'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91 9876543210',
            'id': 'profile_phone'
        })
    )
    district = forms.ChoiceField(
        choices=[('', '-- Select Preferred District --')] + TouristProfile.DISTRICT_CHOICES,
        required=False,
        label="Preferred Kerala District",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'profile_district'
        })
    )
    address = forms.CharField(
        required=False,
        label="Home / Residential Address",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Your postal or residential address',
            'id': 'profile_address'
        })
    )
    location_address = forms.CharField(
        max_length=255,
        required=False,
        label="GPS Selected Landmark / Location",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Fort Kochi, Kochi or Munnar Tea Garden',
            'id': 'profile_location_address'
        })
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        label="GPS Latitude",
        widget=forms.NumberInput(attrs={
            'class': 'form-control font-monospace',
            'step': '0.000001',
            'placeholder': 'e.g. 10.850516',
            'id': 'profile_latitude'
        })
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        label="GPS Longitude",
        widget=forms.NumberInput(attrs={
            'class': 'form-control font-monospace',
            'step': '0.000001',
            'placeholder': 'e.g. 76.271080',
            'id': 'profile_longitude'
        })
    )

    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat is not None:
            if lat < -90 or lat > 90:
                raise ValidationError("Latitude must be between -90.0 and 90.0 degrees.")
        return lat

    def clean_longitude(self):
        lng = self.cleaned_data.get('longitude')
        if lng is not None:
            if lng < -180 or lng > 180:
                raise ValidationError("Longitude must be between -180.0 and 180.0 degrees.")
        return lng

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')

        if (lat is not None and lng is None) or (lat is None and lng is not None):
            raise ValidationError("Both latitude and longitude must be provided together, or leave both empty.")

        return cleaned_data
