from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ModelOnboardingForm
from .services import BlurService
from .models import ModelProfile

class OnboardingView(LoginRequiredMixin, View):
    def get(self, request):
        form = ModelOnboardingForm()
        return render(request, 'models_app/onboarding.html', {'form': form})

    def post(self, request):
        form = ModelOnboardingForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            form.save_m2m()
            
            # Re-fetch or verify
            print(f"Profile saved. Locations: {profile.locations.all()}")
            
            if request.POST.get('blur_face') == 'on' and 'pfp' in request.FILES:
                blurrer = BlurService()
                blurred_image = blurrer.process_image(request.FILES['pfp'])
                profile.pfp.save(request.FILES['pfp'].name, blurred_image, save=True)
            
            return redirect('/')
        else:
            print(f"Form errors: {form.errors}")
            return render(request, 'models_app/onboarding.html', {'form': form})
