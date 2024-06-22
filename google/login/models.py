from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    """Профиль ползователя"""
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Category(models.Model):
    """Категория"""
    name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    image = models.ImageField(upload_to='category_images', blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Wallet(models.Model):
    """Кошелек"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet of {self.user.email} - Balance: {self.balance}"


class Expense(models.Model):
    """Расходы"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='expenses')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(verbose_name='сумма расхода', max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    comments = models.TextField(blank=True, null=True, verbose_name='комментарии к расходу')

    def __str__(self):
        return f"{self.amount} - {self.category.name} on {self.date}"


class Income(models.Model):
    """Даход"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='incomes')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='incomes')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='incomes')
    date = models.DateField()
    comments = models.TextField(blank=True, null=True, verbose_name='комментарии к доходу')

    def __str__(self):
        return f"{self.amount} - {self.category.name} on {self.date}"


"""фунция для обловления баланса из кошелка"""
@receiver(post_save, sender=Expense)
def update_wallet_balance_on_expense_save(sender, instance, created, **kwargs):
    if created:
        instance.wallet.balance -= instance.amount
        instance.wallet.save()
    else:
        previous = Expense.objects.get(pk=instance.pk)
        difference = previous.amount - instance.amount
        instance.wallet.balance += difference
        instance.wallet.save()


@receiver(post_save, sender=Income)
def update_wallet_balance_on_income_save(sender, instance, created, **kwargs):
    if created:
        instance.wallet.balance += instance.amount
        instance.wallet.save()
    else:
        previous = Income.objects.get(pk=instance.pk)
        difference = instance.amount - previous.amount
        instance.wallet.balance += difference
        instance.wallet.save()


