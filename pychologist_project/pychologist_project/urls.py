from django.contrib import admin
from django.urls import path, include, re_path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


from rest_framework.routers import DefaultRouter
from patients.core.infrastructure.api.views.views import PatientViewSet
from therapists.core.infrastructure.adapters.views.therapist_manager_views import TherapistViewSet
from core.log.views import AuditLogListView
from payments.core.infrastructure.api.views.payment_manager_view import PaymentApiView
from therapy.views import TherapySessionViewSet

from users.core.presentation.api.controllers.user_manager_views import UserViewSet
from users.core.presentation.api.controllers.auth_views import SignupView, LoginView, LogoutView, RefreshSessionView
from users.core.presentation.api.controllers.user_views import HomeView, ProfileView

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
    path('payments/', PaymentApiView.as_view(), name='payment-search'),
    path('payments/', PaymentApiView.as_view(), name='payment-create'),
    path('payments/<int:payment_id>/', PaymentApiView.as_view(), name='payment-retrieve'),
    path('payments/<int:payment_id>/', PaymentApiView.as_view(), name='payment-update'),
    path('payments/<int:payment_id>/', PaymentApiView.as_view(), name='payment-delete'),

    # Audit log
    path('audit-logs/', AuditLogListView.as_view(), name='audit-log-list'),

]