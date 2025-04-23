from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter

from patients.infrastructure.api.views.patient_views import PatientViewSet

from core.log.views import AuditLogListView

from therapists.core.infrastructure.adapters.views.therapist_manager_views import TherapistViewSet

from payments.core.infrastructure.api.views.payment_manager_view import PaymentViewSet

from therapy.views import TherapySessionViewSet

from users.core.presentation.api.controllers.user_manager_views import UserViewSet
from users.core.presentation.api.controllers.auth_views import SignupView, LoginView, LogoutView, RefreshSessionView
from users.core.presentation.api.controllers.user_views import HomeView, ProfileView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'therapists', TherapistViewSet, basename='therapist')
router.register(r'therapy-sessions', TherapySessionViewSet, basename='therapy-session')
router.register(r'payments', PaymentViewSet, basename='payment')

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

    # Audit log
    path('audit-logs/', AuditLogListView.as_view(), name='audit-log-list'),

]