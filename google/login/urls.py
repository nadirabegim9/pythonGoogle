from django.urls import path, include
from .views import *

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    # Категории
    path('categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category_list'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='category_detail'),

    # Кошельки
    path('wallets/', WalletViewSet.as_view({'get': 'list', 'post': 'create'}), name='wallet_list'),
    path('wallets/<int:pk>/', WalletViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='wallet_detail'),

    # Расходы
    path('expenses/', ExpenseViewSet.as_view({'get': 'list', 'post': 'create'}), name='expense_list'),
    path('expenses/<int:pk>/', ExpenseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='expense_detail'),

    # Доходы
    path('incomes/', IncomeViewSet.as_view({'get': 'list', 'post': 'create'}), name='income_list'),
    path('incomes/<int:pk>/', IncomeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='income_detail'),

    # Бюджет
    path('budget/', BudgetViewSet.as_view({'get': 'list', 'post': 'create'}), name='budget_list'),
    path('budget/<int:pk>/', BudgetViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='budget_detail'),
]

