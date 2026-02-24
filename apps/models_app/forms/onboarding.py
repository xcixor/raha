from django import forms
from ..models import ModelProfile, Service, Location

class ModelOnboardingForm(forms.ModelForm):
    PROTECTION_CHOICES = [
        ('none', 'None'),
        ('blur', 'Black Smudge'),
        ('emoji', 'Hide with Emoji 😎'),
    ]
    
    privacy_protection = forms.ChoiceField(
        choices=PROTECTION_CHOICES,
        initial='none',
        widget=forms.RadioSelect(attrs={'class': 'hidden peer'}),
        label="Face Protection"
    )
    
    primary_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=True,
        empty_label="Select your primary location",
        widget=forms.Select(attrs={'class': 'w-full bg-gray-900 border border-gray-700 text-white rounded p-2 focus:border-pink-500 outline-none'})
    )
    
    nearby_locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = ModelProfile
        fields = ('model_name', 'pfp', 'short_summary', 'orientation', 'description', 'primary_location', 'nearby_locations', 'services')
        widgets = {
            'short_summary': forms.TextInput(attrs={
                'class': 'w-full bg-gray-900 border border-gray-700 text-white rounded p-2 focus:border-pink-500 outline-none',
                'placeholder': 'E.g. The hottest model in Nairobi'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ModelNameUpdateForm(forms.ModelForm):
    class Meta:
        model = ModelProfile
        fields = ['model_name']
        widgets = {
            'model_name': forms.TextInput(attrs={'class': 'w-full bg-gray-900 border border-gray-700 text-white rounded p-2 focus:border-pink-500 outline-none'}),
        }

class ShortSummaryUpdateForm(forms.ModelForm):
    class Meta:
        model = ModelProfile
        fields = ['short_summary']
        widgets = {
            'short_summary': forms.TextInput(attrs={'class': 'w-full bg-gray-900 border border-gray-700 text-white rounded p-2 focus:border-pink-500 outline-none'}),
        }

class DescriptionUpdateForm(forms.ModelForm):
    class Meta:
        model = ModelProfile
        fields = ['description']

class OrientationUpdateForm(forms.ModelForm):
    class Meta:
        model = ModelProfile
        fields = ['orientation']

class LocationUpdateForm(forms.ModelForm):
    class Meta:
        model = ModelProfile
        fields = ['primary_location', 'nearby_locations']

class ServicesUpdateForm(forms.ModelForm):
    class Meta:
        model = ModelProfile
        fields = ['services']

class GalleryUploadForm(forms.ModelForm):
    class Meta:
        model = ModelProfile
        fields = []
