from django.contrib import admin

from .models import User, Lead, Agent, UserProfile, Category

admin.site.register(User)
admin.site.register(Lead)
admin.site.register(Agent)  # <--- This line was added
admin.site.register(UserProfile)
admin.site.register(Category)