from django import forms
from .models import ModelProfile, Service, Location

class ModelOnboardingForm(forms.ModelForm):
    blur_face = forms.BooleanField(required=False, label="Blur my face in PFP")
    
    # Use ModelMultipleChoiceField with CheckboxSelectMultiple for the UI
    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = ModelProfile
        fields = ('model_name', 'pfp', 'orientation', 'description')
