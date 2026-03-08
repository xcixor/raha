from django.db import models
from .profile import ModelProfile

class ModelMedia(models.Model):
    profile = models.ForeignKey(ModelProfile, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='profiles/media/')
    is_video = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
