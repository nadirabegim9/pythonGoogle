from rest_framework import serializers
from .models import *
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model


User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'last_name', 'password')

class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'last_name', 'password')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('user',)

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('user',)

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'date', 'comments', 'user', 'wallet', 'category']
        read_only_fields = ('user', 'wallet')

    def validate_category(self, value):
        if not Category.objects.filter(user=self.context['request'].user, id=value.id).exists():
            raise serializers.ValidationError("Вы можете выбрать только созданные категории..")
        return value

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['id', 'amount', 'date', 'comments', 'user', 'wallet', 'category']
        read_only_fields = ('user', 'wallet')

    def validate_category(self, value):
        if not Category.objects.filter(user=self.context['request'].user, id=value.id).exists():
            raise serializers.ValidationError("Вы можете выбрать только созданные категории.")
        return value

class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finance
        fields = '__all__'
        read_only_fields = ('user', 'is_achieved')

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ('user',)

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ('user',)

class ReportIncomeSerializer(serializers.ModelSerializer):
    transaction_type = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    balance = serializers.CharField(source='wallet.balance', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Income
        fields = ['id', 'amount', 'date', 'comments', 'username', 'balance', 'category', 'transaction_type']

    def validate_category(self, value):
        if not Category.objects.filter(user=self.context['request'].user, id=value.id).exists():
            raise serializers.ValidationError("Вы можете выбрать только созданные категории.")
        return value

    def get_transaction_type(self, obj):
        return 'income'

class ReportExpenseSerializer(serializers.ModelSerializer):
    transaction_type = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    balance = serializers.CharField(source='wallet.balance', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'amount', 'date', 'comments', 'username', 'balance', 'category', 'transaction_type']

    def validate_category(self, value):
        if not Category.objects.filter(user=self.context['request'].user, id=value.id).exists():
            raise serializers.ValidationError("Вы можете выбрать только созданные категории.")
        return value

    def get_transaction_type(self, obj):
        return 'expense'

