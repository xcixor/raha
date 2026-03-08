import re
from django import forms
from django.core.exceptions import ValidationError
from ..models import User

class UserRegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '0700000000', 'maxlength': '10'}),
        help_text="Exactly 10 digits starting with 07"
    )
    confirm_phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Confirm phone number'}),
        label="Confirm Mobile Number"
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ('phone_number', 'confirm_phone_number', 'password')

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Normalize: strip spaces/dashes
        normalized = re.sub(r'[^\d]', '', phone)
        
        if not re.match(r'^07\d{8}$', normalized):
            raise ValidationError("Enter a valid 10-digit phone number starting with 07.")
            
        return normalized

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone_number")
        confirm_phone = cleaned_data.get("confirm_phone_number")

        if phone and confirm_phone and phone != confirm_phone:
            self.add_error('confirm_phone_number', "Phone numbers do not match.")
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0700000000'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        normalized = re.sub(r'[^\d]', '', phone)
        return normalized
