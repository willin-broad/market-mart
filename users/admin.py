from django.contrib import admin

from .models import Follow, Message, Profile

# Register your models here.

admin.site.register(Follow)
admin.site.register(Message)
admin.site.register(Profile)
