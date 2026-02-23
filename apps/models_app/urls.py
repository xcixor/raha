from django.urls import path
from . import views, views_htmx

app_name = 'models'

urlpatterns = [
    path('', views.ModelListView.as_view(), name='list'),
    path('onboarding/', views.OnboardingView.as_view(), name='onboarding'),
    path('profile/<slug:slug>/', views.ModelDetailView.as_view(), name='profile_detail'),
    path('gallery/upload/', views.GalleryUploadView.as_view(), name='gallery_upload'),
    path('htmx/nearby-locations/', views_htmx.get_nearby_locations, name='nearby_locations_htmx'),
]
