from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TouristRegistrationForm, TouristLoginForm, TouristProfileEditForm
from .models import TouristProfile

def register_view(request):
    """Handles Tourist Registration."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = TouristRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Welcome to Kerala Smart Tourism, {user.first_name or user.username}! Your account has been created successfully. You can now log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = TouristRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handles Tourist Login using username OR email."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = TouristLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email'].strip()
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=username_or_email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if remember_me:
                        # 2 weeks session expiry
                        request.session.set_expiry(1209600)
                    else:
                        # Expire when browser closes
                        request.session.set_expiry(0)

                    messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                    next_url = request.GET.get('next')
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    return redirect('accounts:dashboard')
                else:
                    messages.error(request, "Your account is currently disabled. Please contact support.")
            else:
                messages.error(request, "Invalid username/email or password. Please try again.")
        else:
            messages.error(request, "Please enter both your username/email and password.")
    else:
        form = TouristLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logs the tourist out and redirects to login page with feedback."""
    logout(request)
    messages.info(request, "You have been logged out successfully. Have a safe journey!")
    return redirect('accounts:login')


@login_required(login_url='accounts:login')
def dashboard_view(request):
    """Protected Tourist Dashboard."""
    profile, _ = TouristProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
    })


@login_required(login_url='accounts:login')
def profile_edit_view(request):
    """Allows tourists to edit their profile information and choose their GPS location using Leaflet."""
    profile, _ = TouristProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TouristProfileEditForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned = form.cleaned_data
            # Update User fields
            request.user.first_name = cleaned['first_name']
            request.user.last_name = cleaned['last_name']
            request.user.save()

            # Update TouristProfile fields
            profile.phone_number = cleaned.get('phone_number', '')
            profile.district = cleaned.get('district', '')
            profile.address = cleaned.get('address', '')
            profile.location_address = cleaned.get('location_address', '')
            profile.latitude = cleaned.get('latitude')
            profile.longitude = cleaned.get('longitude')
            if 'profile_image' in request.FILES:
                profile.profile_image = request.FILES['profile_image']
            profile.save()

            messages.success(request, "Your profile and GPS location settings have been updated successfully!")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone_number': profile.phone_number,
            'district': profile.district,
            'address': profile.address,
            'location_address': profile.location_address,
            'latitude': profile.latitude,
            'longitude': profile.longitude,
        }
        form = TouristProfileEditForm(initial=initial_data)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'profile': profile,
    })
