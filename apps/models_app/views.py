from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from .forms import ModelOnboardingForm
from .services import BlurService
from .services_verification import VerificationService
from .models import ModelProfile, ModelMedia

class OnboardingView(LoginRequiredMixin, View):
    def get(self, request):
        # If profile exists, populate form
        profile = getattr(request.user, 'profile', None)
        form = ModelOnboardingForm(instance=profile)
        return render(request, 'models_app/onboarding.html', {'form': form})

    @transaction.atomic
    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        form = ModelOnboardingForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            form.save_m2m()
            
            protection_mode = form.cleaned_data.get('privacy_protection')
            if protection_mode in ['blur', 'emoji'] and 'pfp' in request.FILES:
                blurrer = BlurService()
                request.FILES['pfp'].seek(0)
                protected_image = blurrer.process_image(request.FILES['pfp'], mode=protection_mode)
                profile.pfp.save(request.FILES['pfp'].name, protected_image, save=True)
            
            if request.headers.get('HX-Request'):
                response = HttpResponse('')
                response['HX-Redirect'] = reverse('root')
                return response
                
            return redirect('/')
        return render(request, 'models_app/onboarding.html', {'form': form})

class ProfileDetailView(LoginRequiredMixin, View):
    def get(self, request):
        profile = get_object_or_404(ModelProfile, user=request.user)
        return render(request, 'models_app/profile_detail.html', {'profile': profile})

class GalleryUploadView(LoginRequiredMixin, View):
    def post(self, request):
        profile = get_object_or_404(ModelProfile, user=request.user)
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            return HttpResponse("No file uploaded", status=400)

        # Basic video detection based on extension/mime
        is_video = uploaded_file.content_type.startswith('video/')
        
        media = ModelMedia(
            profile=profile,
            file=uploaded_file,
            is_video=is_video
        )

        # Apply protection if it's an image and requested
        protection_mode = request.POST.get('privacy_protection', 'none')
        if not is_video and protection_mode in ['blur', 'emoji']:
            blurrer = BlurService()
            protected_image = blurrer.process_image(uploaded_file, mode=protection_mode)
            media.file.save(uploaded_file.name, protected_image, save=False)

        media.save()

        # If it's an HTMX request, return a fragment
        if request.headers.get('HX-Request'):
            return render(request, 'models_app/partials/media_item.html', {'media': media})

        return redirect('/') # Fallback
