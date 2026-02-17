from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .forms import ModelOnboardingForm
from .services import BlurService
from .models import ModelProfile, ModelMedia

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
            
            if request.POST.get('blur_face') == 'on' and 'pfp' in request.FILES:
                blurrer = BlurService()
                blurred_image = blurrer.process_image(request.FILES['pfp'])
                profile.pfp.save(request.FILES['pfp'].name, blurred_image, save=True)
            
            return redirect('/')
        return render(request, 'models_app/onboarding.html', {'form': form})

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

        # Apply blurring if it's an image and requested
        if not is_video and request.POST.get('blur_face') == 'on':
            blurrer = BlurService()
            blurred_image = blurrer.process_image(uploaded_file)
            media.file.save(uploaded_file.name, blurred_image, save=False)

        media.save()

        # If it's an HTMX request, return a fragment
        if request.headers.get('HX-Request'):
            return render(request, 'models_app/partials/media_item.html', {'media': media})

        return redirect('/') # Fallback
