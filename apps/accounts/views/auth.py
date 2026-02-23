from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, authenticate, logout
from ..forms import UserRegistrationForm, LoginForm
from ..models import User

class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form, 'title': 'Join Raha', 'button_text': 'Register'})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('models:onboarding')
        return render(request, 'accounts/register.html', {'form': form, 'title': 'Join Raha', 'button_text': 'Register'})

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'accounts/register.html', {'form': form, 'title': 'Login to Raha', 'button_text': 'Login'})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            user = authenticate(request, phone_number=phone, password=password)
            if user:
                login(request, user)
                return redirect('/')
            form.add_error(None, "Invalid phone or password")
        return render(request, 'accounts/register.html', {'form': form, 'title': 'Login to Raha', 'button_text': 'Login'})

class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('accounts:login')
