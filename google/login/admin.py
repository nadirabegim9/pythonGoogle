from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(CustomUser)
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(Budget)
admin.site.register(Reminder)
admin.site.register(Finance)

