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
            
            # Handle Optional Blurring
            if request.POST.get('blur_face') == 'on' and 'pfp' in request.FILES:
                blurrer = BlurService()
                blurred_image = blurrer.process_image(request.FILES['pfp'])
                profile.pfp.save(request.FILES['pfp'].name, blurred_image, save=False)
            
            profile.save()
            # M2M needs save_m2m() or manual assignment after profile.save()
            form.save_m2m()
            
            return redirect('/')
        return render(request, 'models_app/onboarding.html', {'form': form})
