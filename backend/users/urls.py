from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profile', UserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
]
