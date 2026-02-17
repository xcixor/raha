from django.urls import path
from . import views

app_name = 'models'

urlpatterns = [
    path('onboarding/', views.OnboardingView.as_view(), name='onboarding'),
]
