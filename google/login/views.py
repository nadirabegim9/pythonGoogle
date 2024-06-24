from rest_framework import viewsets, permissions
from .models import *
from .serializers import *
import matplotlib.pyplot as plt
import seaborn as sns
from rest_framework.response import Response
from rest_framework.views import APIView
from.models import Expense, Income
from.serializers import ExpenseSerializer, IncomeSerializer
from django.contrib.auth.decorators import login_required
from io import BytesIO
from django.utils.decorators import method_decorator
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login


from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import StreamingHttpResponse
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import pandas as pd
from .models import Expense, Income

class VisualAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the user's expenses and incomes
        expenses = Expense.objects.filter(user=request.user)
        incomes = Income.objects.filter(user=request.user)

        # Convert QuerySets to DataFrames
        expenses_df = pd.DataFrame(list(expenses.values('amount', 'category', 'date')))
        incomes_df = pd.DataFrame(list(incomes.values('amount', 'category', 'date')))

        # Generate the visualizations
        fig, ax = plt.subplots(2, 2, figsize=(12, 8))

        # Expenses by category
        sns.countplot(x='category', data=expenses_df, ax=ax[0, 0])
        ax[0, 0].set_title('Expenses by Category')

        # Incomes by category
        sns.countplot(x='category', data=incomes_df, ax=ax[0, 1])
        ax[0, 1].set_title('Incomes by Category')

        # Expenses over time
        sns.lineplot(x='date', y='amount', data=expenses_df, ax=ax[1, 0])
        ax[1, 0].set_title('Expenses over Time')

        # Incomes over time
        sns.lineplot(x='date', y='amount', data=incomes_df, ax=ax[1, 1])
        ax[1, 1].set_title('Incomes over Time')

        # Convert the figure to a PNG image
        img = BytesIO()
        fig.savefig(img, format='png')
        img.seek(0)

        # Return the image as a streaming response
        response = StreamingHttpResponse(img, content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="analytics.png"'
        return response

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated]  # Пример разрешений - замените на необходимые


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
