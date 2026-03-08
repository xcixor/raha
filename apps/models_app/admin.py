from django.contrib import admin
from .models import County, LocationGroup, Service, Location, ModelProfile, ModelMedia

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(LocationGroup)
class LocationGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'county', 'slug')
    list_filter = ('county',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'is_primary', 'slug')
    list_filter = ('group', 'is_primary')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ModelMediaInline(admin.TabularInline):
    model = ModelMedia
    extra = 1

@admin.register(ModelProfile)
class ModelProfileAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'user', 'is_verified', 'is_active', 'primary_location', 'created_at')
    list_filter = ('is_verified', 'is_active', 'primary_location', 'orientation')
    search_fields = ('model_name', 'user__phone_number')
    prepopulated_fields = {'slug': ('model_name',)}
    inlines = [ModelMediaInline]
