from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CurrentUserAPIView, GoogleLoginAPIView

urlpatterns = [
    path('google/login/', GoogleLoginAPIView.as_view(), name='google-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', CurrentUserAPIView.as_view(), name='current-user'),
]
