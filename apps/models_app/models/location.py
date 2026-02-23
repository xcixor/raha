from django.db import models

class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Counties"

    def __str__(self):
        return self.name

class LocationGroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='groups')

    def __str__(self):
        return f"{self.name} ({self.county.name})"

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_primary = models.BooleanField(default=False)
    group = models.ForeignKey(LocationGroup, on_delete=models.SET_NULL, null=True, related_name='locations')

    def __str__(self):
        return self.name
