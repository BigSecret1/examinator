import logging

from .actions import GoogleOAuthAction

logger = logging.getLogger(__name__)


class GoogleOAuthInterface:

    @staticmethod
    def authenticate(credential):
        try:
            return GoogleOAuthAction.authenticate(credential)
        except ValueError as exc:
            logger.warning('Google OAuth verification failed: %s', exc)
            return {'error': str(exc)}
        except Exception as exc:
            logger.exception('Google OAuth unexpected error')
            return {'error': str(exc)}
