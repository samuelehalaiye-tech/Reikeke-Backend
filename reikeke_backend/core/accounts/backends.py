from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class PhoneNumberBackend(ModelBackend):
    """
    Custom authentication backend that uses phone_number as USERNAME_FIELD
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.info(f"PhoneNumberBackend.authenticate() called with username={username}")
        
        try:
            # Try to find user by phone_number
            user = User.objects.get(phone_number=username)
            logger.info(f"User found in database: {user.id}, phone_number={user.phone_number}")
        except User.DoesNotExist:
            logger.error(f"User with phone_number={username} not found")
            return None

        # Check password
        if user.check_password(password):
            logger.info(f"Password check passed for user {user.id}")
        else:
            logger.error(f"Password check failed for user {user.id}")
        
        if user.check_password(password) and self.user_can_authenticate(user):
            logger.info(f"Authentication successful for user {user.id}")
            return user
        
        logger.error(f"Authentication failed. check_password={user.check_password(password)}, user_can_authenticate={self.user_can_authenticate(user)}")
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
