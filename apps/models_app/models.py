from django.db import models
from django.conf import settings

class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ModelProfile(models.Model):
    ORIENTATION_CHOICES = [
        ('straight', 'Straight'),
        ('bisexual', 'Bisexual'),
        ('gay', 'Gay'),
        ('lesbian', 'Lesbian'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    model_name = models.CharField(max_length=100)
    pfp = models.ImageField(upload_to='profiles/pfp/')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    # Switch to M2M for proper fixture usage and relations
    locations = models.ManyToManyField(Location, related_name='models', blank=True)
    services = models.ManyToManyField(Service, related_name='models', blank=True)
    
    orientation = models.CharField(max_length=20, choices=ORIENTATION_CHOICES, default='straight')
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model_name

class ModelMedia(models.Model):
    profile = models.ForeignKey(ModelProfile, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='profiles/media/')
    is_video = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
