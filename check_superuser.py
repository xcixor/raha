import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User

superusers = User.objects.filter(is_superuser=True)
if not superusers.exists():
    print("No superuser found.")
else:
    for u in superusers:
        print(f"Superuser: {u.phone_number}")
