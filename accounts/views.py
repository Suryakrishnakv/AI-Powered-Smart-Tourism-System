from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TouristRegistrationForm, TouristLoginForm

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
    profile = getattr(request.user, 'tourist_profile', None)
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
    })
