from django.urls import path
from . import views

app_name = 'models'

urlpatterns = [
    path('', views.ModelListView.as_view(), name='list'),
    path('onboarding/', views.OnboardingView.as_view(), name='onboarding'),
    path('profile/<slug:slug>/', views.ModelDetailView.as_view(), name='profile_detail'),
    path('gallery/upload/', views.GalleryUploadView.as_view(), name='gallery_upload'),
    path('gallery/remove/<int:pk>/', views.GalleryRemoveView.as_view(), name='gallery_remove'),
    path('htmx/nearby-locations/', views.get_nearby_locations, name='nearby_locations_htmx'),
    path('htmx/filter-locations/', views.filter_locations_by_county, name='filter_locations_htmx'),
    
    # Public Discovery Views
    path('discover/model/<slug:slug>/', views.ModelPublicDetailView.as_view(), name='public_profile_detail'),

    # Inline Editing Endpoints
    path('profile/<slug:slug>/edit/name/', views.ModelNameUpdateView.as_view(), name='edit_name'),
    path('profile/<slug:slug>/edit/summary/', views.ShortSummaryUpdateView.as_view(), name='edit_summary'),
    path('profile/<slug:slug>/edit/description/', views.DescriptionUpdateView.as_view(), name='edit_description'),
    path('profile/<slug:slug>/edit/orientation/', views.OrientationUpdateView.as_view(), name='edit_orientation'),
    path('profile/<slug:slug>/edit/location/', views.LocationUpdateView.as_view(), name='edit_location'),
    path('profile/<slug:slug>/edit/services/', views.ServicesUpdateView.as_view(), name='edit_services'),
    path('profile/<slug:slug>/edit/pfp/', views.PFPUpdateView.as_view(), name='edit_pfp'),
]
