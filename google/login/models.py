from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.core.mail import send_mail


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


@receiver(post_save, sender=CustomUser)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


class Expense(models.Model):
    """Расходы"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='expenses')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(verbose_name='сумма расхода', max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    comments = models.TextField(blank=True, null=True, verbose_name='комментарии к расходу')

    def __str__(self):
        return f"{self.amount} - {self.category.name} on {self.date} - {self.user}"


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

    # Check if any financial goals are achieved
    for goal in instance.user.financial_goals.filter(is_achieved=False):
        goal.check_goal_achievement()


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

    # Check if any financial goals are achieved
    for goal in instance.user.financial_goals.filter(is_achieved=False):
        goal.check_goal_achievement()


class Budget(models.Model):
    """Бюджет"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_budgets')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='установленный бюджет')
    start_date = models.DateField(verbose_name='начало периода')
    end_date = models.DateField(verbose_name='конец периода')

    def __str__(self):
        return f"{self.amount} for {self.category.name} from {self.start_date} to {self.end_date}"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError(_('Дата начала не может быть позже даты окончания.'))


@receiver(post_save, sender=Expense)
def check_budget_threshold(sender, instance, **kwargs):
    budget = Budget.objects.filter(user=instance.user, category=instance.category, start_date__lte=instance.date,
                                   end_date__gte=instance.date).first()
    if budget:
        total_expenses = Expense.objects.filter(user=instance.user, category=instance.category,
                                                date__gte=budget.start_date, date__lte=budget.end_date).aggregate(total=models.Sum('amount'))['total'] or 0
        if total_expenses > budget.amount:
            print(f"Предупреждение: Превышен лимит бюджета для категории {instance.category.name}. Текущие расходы: {total_expenses}, Бюджет: {budget.amount}")


@receiver(pre_save, sender=Expense)
def prevent_exceeding_budget(sender, instance, **kwargs):
    if instance.pk:  # Skip for updates
        return
    budget = Budget.objects.filter(user=instance.user, category=instance.category, start_date__lte=instance.date,
                                   end_date__gte=instance.date).first()
    if budget:
        total_expenses = Expense.objects.filter(user=instance.user, category=instance.category, date__gte=budget.start_date, date__lte=budget.end_date).aggregate(total=models.Sum('amount'))['total'] or 0
        if total_expenses + instance.amount > budget.amount:
            raise ValidationError(f"Добавление этих расходов превысило бы бюджетный лимит для категории {instance.category.name}. Текущие расходы: {total_expenses}, Бюджет: {budget.amount}")


class Reminder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField(verbose_name='начало периода', default=now)
    recurrence_interval = models.CharField(max_length=10, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], blank=True, null=True)

    def __str__(self):
        return self.title


class Finance(models.Model):
    """Финансовая цель"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='financial_goals')
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(default=now)
    end_date = models.DateField()
    is_achieved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.target_amount} by {self.end_date}"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError(_('Дата начала не может быть позже даты окончания.'))

    def check_goal_achievement(self):
        if self.user.wallet.balance >= self.target_amount:
            self.is_achieved = True
            self.save()
            return True
        return False


@receiver(post_save, sender=Finance)
def check_financial_goal(sender, instance, **kwargs):
    if instance.end_date <= now().date() and not instance.is_achieved:
        print(f"Напоминание: Финансовая цель '{instance.name}' близка к своей конечной дате.")

    if instance.check_goal_achievement():
        # Send notification (e.g., email, in-app notification)
        send_mail(
            'Финансовая цель достигнута!',
            f"Поздравляем! Вы достигли своей финансовой цели: {instance.name}.",
            'money@example.com',
            [instance.user.email],
            fail_silently=False,
        )
        print(f"Уведомление: достигнута финансовая цель '{instance.name}'.")

