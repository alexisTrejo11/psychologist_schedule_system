from django.contrib import admin
from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import (
    SignupView,
    LoginView,
    LogoutView,
    RefreshSession,
    UserViewSet,
    PatientViewSet,
    TherapistViewSet,
)


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'therapists', TherapistViewSet, basename='therapist')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh-session/', RefreshSession.as_view(), name='refresh_session'),

    path('', include(router.urls)),
]

