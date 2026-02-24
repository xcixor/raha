from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.urls import reverse
from django.db import transaction
from ..forms import (
    ModelOnboardingForm, 
    ModelNameUpdateForm,
    ShortSummaryUpdateForm,
    DescriptionUpdateForm,
    OrientationUpdateForm,
    LocationUpdateForm,
    ServicesUpdateForm
)
from ..services import BlurService
from ..services_verification import VerificationService
from ..models import ModelProfile, ModelMedia

from django.views.generic import ListView, DetailView, UpdateView
from ..models import ModelProfile, ModelMedia

class ModelListView(ListView):
    model = ModelProfile
    template_name = 'models_app/list.html'
    context_object_name = 'models'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        return ModelProfile.objects.filter(is_active=True).select_related('primary_location').order_by('-created_at')

class ModelDetailView(DetailView):
    model = ModelProfile
    template_name = 'models_app/profile_detail.html'
    context_object_name = 'profile'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the current user is the owner of this profile
        context['is_owner'] = self.request.user.is_authenticated and self.request.user == self.object.user
        return context

class BaseProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ModelProfile
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.display_template, {
                'profile': self.object, 
                'is_owner': True
            })
        return response

class ModelNameUpdateView(BaseProfileUpdateView):
    form_class = ModelNameUpdateForm
    template_name = 'models_app/partials/inline_edit_model_name.html'
    display_template = 'models_app/partials/inline_display_model_name.html'

class ShortSummaryUpdateView(BaseProfileUpdateView):
    form_class = ShortSummaryUpdateForm
    template_name = 'models_app/partials/inline_edit_short_summary.html'
    display_template = 'models_app/partials/inline_display_short_summary.html'

class DescriptionUpdateView(BaseProfileUpdateView):
    form_class = DescriptionUpdateForm
    template_name = 'models_app/partials/inline_edit_description.html'
    display_template = 'models_app/partials/inline_display_description.html'

class OrientationUpdateView(BaseProfileUpdateView):
    form_class = OrientationUpdateForm
    template_name = 'models_app/partials/inline_edit_orientation.html'
    display_template = 'models_app/partials/inline_display_orientation.html'

class LocationUpdateView(BaseProfileUpdateView):
    form_class = LocationUpdateForm
    template_name = 'models_app/partials/inline_edit_location.html'
    display_template = 'models_app/partials/inline_display_location.html'

class ServicesUpdateView(BaseProfileUpdateView):
    form_class = ServicesUpdateForm
    template_name = 'models_app/partials/inline_edit_services.html'
    display_template = 'models_app/partials/inline_display_services.html'

class PFPUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        profile = get_object_or_404(ModelProfile, slug=self.kwargs['slug'])
        return self.request.user == profile.user

    def get(self, request, slug):
        profile = get_object_or_404(ModelProfile, slug=slug)
        return render(request, 'models_app/partials/inline_edit_pfp.html', {'profile': profile})

    def post(self, request, slug):
        profile = get_object_or_404(ModelProfile, slug=slug)
        pfp_file = request.FILES.get('pfp')
        
        if pfp_file:
            protection_mode = request.POST.get('privacy_protection', 'none')
            if protection_mode in ['blur', 'emoji']:
                blurrer = BlurService()
                pfp_file.seek(0)
                protected_image = blurrer.process_image(pfp_file, mode=protection_mode)
                profile.pfp.save(pfp_file.name, protected_image, save=True)
            else:
                profile.pfp = pfp_file
                profile.save()
        
        return render(request, 'models_app/partials/inline_display_pfp.html', {
            'profile': profile, 
            'is_owner': True
        })

class GalleryRemoveView(LoginRequiredMixin, View):
    def delete(self, request, pk):
        media = get_object_or_404(ModelMedia, pk=pk, profile__user=request.user)
        media.delete()
        return HttpResponse("")

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
            profile.is_active = True  # Auto-activate for now so they show up on Discover
            
            protection_mode = form.cleaned_data.get('privacy_protection')
            pfp_file = request.FILES.get('pfp')
            
            if pfp_file and protection_mode in ['blur', 'emoji']:
                blurrer = BlurService()
                pfp_file.seek(0)
                protected_image = blurrer.process_image(pfp_file, mode=protection_mode)
                # Overwrite the pfp with the protected version before saving
                profile.pfp.save(pfp_file.name, protected_image, save=False)
            
            profile.save()
            form.save_m2m()
            
            if request.headers.get('HX-Request'):
                response = HttpResponse('')
                response['HX-Redirect'] = reverse('root')
                return response
                
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
