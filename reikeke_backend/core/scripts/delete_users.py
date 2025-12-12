from django.apps import apps
from django.db import transaction
User = apps.get_model('accounts', 'User')
Token = __import__('rest_framework.authtoken.models', fromlist=['Token']).Token

print('BEFORE_USER_COUNT:', User.objects.count())
print('BEFORE_TOKEN_COUNT:', Token.objects.count())

with transaction.atomic():
    Token.objects.all().delete()
    User.objects.all().delete()

print('AFTER_USER_COUNT:', User.objects.count())
print('AFTER_TOKEN_COUNT:', Token.objects.count())
