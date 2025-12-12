import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User
from rest_framework.authtoken.models import Token

print("USER_COUNT:", User.objects.count())
print("TOKEN_COUNT:", Token.objects.count())
print(json.dumps(list(User.objects.values('id','phone_number')[:100])))
