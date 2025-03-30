from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from therapy.views import TherapySessionViewSet
from users.views.patient_views import PatientViewSet
from users.views.therapist_views import TherapistViewSet
from users.views.user_views import UserViewSet
from users.views.auth_views import (
    SignupView,
    LoginView,
    LogoutView,
    RefreshSessionView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'therapists', TherapistViewSet, basename='therapist')
router.register(r'therapy-sessions', TherapySessionViewSet, basename='therapy-session')


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh-session/', RefreshSessionView.as_view(), name='refresh_session'),

    # General APIs
    path('', include(router.urls)),

    # Custom endpoints for PatientViewSet
    path(
        'patients/<int:pk>/soft-delete/',
        PatientViewSet.as_view({'post': 'soft_delete'}),
        name='patient-soft-delete',
    ),
    path(
        'patients/deleted/',
        PatientViewSet.as_view({'get': 'get_deleted_patients'}),
        name='patient-deleted',
    ),
    path(
        'patients/search/',
        PatientViewSet.as_view({'get': 'search_patients'}),
        name='patient-search',
    ),
]