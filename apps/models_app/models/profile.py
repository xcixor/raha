from django.db import models
from django.conf import settings
from .location import Location
from .service import Service

class ModelProfile(models.Model):
    ORIENTATION_CHOICES = [
        ('straight', 'Straight'),
        ('bisexual', 'Bisexual'),
        ('gay', 'Gay'),
        ('lesbian', 'Lesbian'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    model_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    pfp = models.ImageField(upload_to='profiles/pfp/')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    primary_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='primary_models')
    nearby_locations = models.ManyToManyField(Location, related_name='nearby_models', blank=True)
    
    services = models.ManyToManyField(Service, related_name='models', blank=True)
    
    orientation = models.CharField(max_length=20, choices=ORIENTATION_CHOICES, default='straight')
    short_summary = models.CharField(max_length=40)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.model_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.model_name

    @property
    def whatsapp_number(self):
        """Returns phone number in 2547XXXXXXXX format"""
        phone = self.user.phone_number
        if phone.startswith('0'):
            return f"254{phone[1:]}"
        if phone.startswith('+'):
            return phone[1:]
        return phone
