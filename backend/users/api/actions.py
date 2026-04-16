from django.conf import settings
from django.contrib.auth import get_user_model
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import UserProfile

User = get_user_model()


class GoogleOAuthAction:

    @staticmethod
    def verify_token(credential):
        try:
            id_info = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID,
            )
        except ValueError as e:
            raise ValueError(f'Invalid token: {e}')

        if id_info['iss'] not in ('accounts.google.com', 'https://accounts.google.com'):
            raise ValueError('Invalid issuer.')

        return {
            'email': id_info['email'],
            'google_id': id_info['sub'],
            'first_name': id_info.get('given_name', ''),
            'last_name': id_info.get('family_name', ''),
            'avatar_url': id_info.get('picture', ''),
        }

    @staticmethod
    def get_or_create_user(profile):
        try:
            user_profile = UserProfile.objects.select_related('user').get(
                google_id=profile['google_id'],
            )
            return user_profile.user
        except UserProfile.DoesNotExist:
            user = User.objects.create_user(
                username=profile['email'].split('@')[0],
                email=profile['email'],
                first_name=profile['first_name'],
                last_name=profile['last_name'],
            )
            UserProfile.objects.create(
                user=user,
                google_id=profile['google_id'],
                avatar_url=profile['avatar_url'],
            )
            return user

    @staticmethod
    def issue_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    @staticmethod
    def authenticate(credential):
        try:
            profile = GoogleOAuthAction.verify_token(credential)
        except ValueError as e:
            raise AuthenticationFailed(str(e))

        user = GoogleOAuthAction.get_or_create_user(profile)
        tokens = GoogleOAuthAction.issue_tokens(user)
        return {'user': user, **tokens}
