from django.contrib import admin
from app.models import *
from django.apps import apps

#register every project table in the admin page
for model in apps.get_app_config('app').models.values():
    admin.site.register(model)
