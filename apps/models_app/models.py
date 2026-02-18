from django.db import models
from django.conf import settings

class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class LocationGroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='groups')

    def __str__(self):
        return f"{self.name} ({self.county.name})"

class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_primary = models.BooleanField(default=False)
    group = models.ForeignKey(LocationGroup, on_delete=models.SET_NULL, null=True, related_name='locations')

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
    model_name = models.CharField(max_length=100, unique=True)
    pfp = models.ImageField(upload_to='profiles/pfp/')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    # Separation of locations: Primary and Nearby
    primary_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='primary_models')
    nearby_locations = models.ManyToManyField(Location, related_name='nearby_models', blank=True)
    
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
