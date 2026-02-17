from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ModelOnboardingForm
from .services import BlurService

class OnboardingView(LoginRequiredMixin, View):
    def get(self, request):
        form = ModelOnboardingForm()
        return render(request, 'models_app/onboarding.html', {'form': form})

    def post(self, request):
        form = ModelOnboardingForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            
            # Save as comma-separated string for SQLite compat
            profile.locations = ",".join(request.POST.getlist('locations'))
            profile.services = ",".join(request.POST.getlist('services'))

            # Handle Optional Blurring
            if request.POST.get('blur_face') == 'on' and 'pfp' in request.FILES:
                blurrer = BlurService()
                blurred_image = blurrer.process_image(request.FILES['pfp'])
                profile.pfp.save(request.FILES['pfp'].name, blurred_image, save=False)
            
            profile.save()
            return redirect('/') # Home or Dashboard
        return render(request, 'models_app/onboarding.html', {'form': form})
