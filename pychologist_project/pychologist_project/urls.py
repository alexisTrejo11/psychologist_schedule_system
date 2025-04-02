from django.contrib import admin
from django.urls import path, include, re_path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from rest_framework.permissions import AllowAny

from rest_framework.routers import DefaultRouter
from therapy.views import TherapySessionViewSet
from patients.views import PatientViewSet
from therapists.views import TherapistViewSet
from users.views.user_manager_views import UserViewSet
from core.auditlog.views import AuditLogListView
from payments.views import PaymentListCreateView, PaymentRetrieveUpdateDestroyView

from users.core.presentation.api.controllers.auth_views import SignupView, LoginView, LogoutView, RefreshSessionView
from users.views.user_views import HomeView, ProfileView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'therapists', TherapistViewSet, basename='therapist')
router.register(r'therapy-sessions', TherapySessionViewSet, basename='therapy-session')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Swagger 
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Auth
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh-session/', RefreshSessionView.as_view(), name='refresh_session'),

    # User
    path('home/', HomeView.as_view(), name='home'),
    path('profiles/', ProfileView.as_view(), name='profile'),

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

    # Payment 
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:payment_id>/', PaymentRetrieveUpdateDestroyView.as_view(), name='payment-detail'),

    # Audit log
    path('audit-logs/', AuditLogListView.as_view(), name='audit-log-list'),

]