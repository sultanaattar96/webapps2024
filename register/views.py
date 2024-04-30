from decimal import Decimal

import requests
from django.conf import settings
from register.models import CustomUser as User
# from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.utils.decorators import method_decorator
from payapp.models import Notification
from .models import Account
from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm, AdminRegisterForm
from django import template
from django.contrib.auth.decorators import login_required, user_passes_test


def home(request):
    return render(request, 'users/home.html')


register = template.Library()


@register.simple_tag
def unread_notification_count(user):
    return Notification.objects.filter(to_user=user, is_read=False).count()


@login_required
def dashboard(request):
    unread_notification_count = Notification.objects.filter(to_user=request.user, is_read=False).count()
    return render(request, 'users/dashboard.html', {'unread_notification_count': unread_notification_count})


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()
            # Additional data such as currency can be accessed from the form's cleaned_data
            currency = form.cleaned_data.get('currency')
            base = 'GBP'
            balance = 1000

            # the system should make the appropriate conversion to assign the right initial amount of money
            if currency != base:
                response = requests.get(
                    f'{settings.BASE_URL}/currency_conversion/conversion/{base}/{currency}/{balance}')
                if response.status_code == 200:
                    balance = Decimal(str(response.json()['converted_amount']))
                    print('acc_balance $$$$$$ -> ', balance)
                else:
                    print(f"Request failed with status code {response.status_code}")
                    return

            user.profile.balance = balance
            user.profile.save()
            # Create an associated account for the user
            Account.objects.create(user=user, currency=currency, balance=balance)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            # Check if email is unique
            email = user_form.cleaned_data.get('email')
            if User.objects.filter(email=email).exclude(username=request.user.username).exists():
                messages.error(request, 'Email address must be unique.')
                return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})

            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
@user_passes_test(lambda u: u.is_staff)
@user_passes_test(lambda u: u.is_superuser)
def register_admin(request):
    form_class = AdminRegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register_admin.html'

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = True
            user.save()
            user.profile.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Admin account created for {username}')
        return render(request, template_name, {'form': form})
    else:
        form = form_class(initial=initial)
        return render(request, template_name, {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff)
@user_passes_test(lambda u: u.is_superuser)
def users_list(request):
    users = User.objects.all()
    return render(request, 'users/users_list.html', {'users': users})

