from django.apps import AppConfig


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'


class YourAppConfig(AppConfig):
    name = 'login'

    def ready(self):
        from .models import Category
        predefined_categories = [
            {'name': 'Food', 'type': Category.EXPENSE},
            {'name': 'Salary', 'type': Category.INCOME},
            {'name': 'Entertainment', 'type': Category.EXPENSE},
            # Добавьте другие категории по необходимости
        ]

        for category_data in predefined_categories:
            Category.objects.get_or_create(**category_data)
