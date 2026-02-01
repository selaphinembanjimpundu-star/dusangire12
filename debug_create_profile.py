import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','dusangire.settings')
import django
django.setup()
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from nutritionist_dashboard.forms import NutritionistProfileForm
from nutritionist_dashboard.models import NutritionistProfile

User = get_user_model()

# create or get user
regular, _ = User.objects.get_or_create(username='regular', defaults={'email':'regular@test.com'})
regular.set_password('testpass123')
regular.save()
client = Client()
logged_in = client.login(username='regular', password='testpass123')
print('logged_in', logged_in)

# simulate POST
data = {'bio':'Test bio','specialization':'Test specialization','max_clients':50}
response = client.post(reverse('nutritionist_dashboard:create_profile'), data, follow=True)
print('response status', response.status_code)
print('redirect chain', response.redirect_chain)
print('profile exists?', NutritionistProfile.objects.filter(user=regular).exists())
print('response content:', response.content.decode('utf-8')[:800])

# check form validity directly
form = NutritionistProfileForm(data)
print('form.is_valid()', form.is_valid())
print('form.errors', form.errors)
