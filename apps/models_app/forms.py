from django import forms
from .models import ModelProfile

class ModelOnboardingForm(forms.ModelForm):
    # Dummy services/locations for the checkbox UI
    # We'll use these to populate the template
    LOCATIONS_LIST = ['Kilimani', 'Westlands', 'Nairobi CBD', 'Mombasa Road', 'Langata']
    SERVICES_LIST = ['Massage', 'Full Service', 'Outcall', 'Incall', 'Dinner Date']

    blur_face = forms.BooleanField(required=False, label="Blur my face in PFP")

    class Meta:
        model = ModelProfile
        fields = ('model_name', 'pfp', 'orientation', 'description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # In a real app, we'd pull these from the DB
        # For now, we'll use these to render the UI checkboxes manually in the template
        # and then collect them into the ArrayField on save
