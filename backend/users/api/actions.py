from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User


class GoogleOAuthAction:

    @staticmethod
    def verify_token(credential):
        id_info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID,
        )

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
            return User.objects.get(google_id=profile['google_id'])
        except User.DoesNotExist:
            return User.objects.create_user(
                username=profile['email'].split('@')[0],
                email=profile['email'],
                google_id=profile['google_id'],
                first_name=profile['first_name'],
                last_name=profile['last_name'],
                avatar_url=profile['avatar_url'],
            )

    @staticmethod
    def issue_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    @staticmethod
    def authenticate(credential):
        profile = GoogleOAuthAction.verify_token(credential)
        user = GoogleOAuthAction.get_or_create_user(profile)
        tokens = GoogleOAuthAction.issue_tokens(user)
        return {'user': user, **tokens}
