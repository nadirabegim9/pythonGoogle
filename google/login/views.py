from rest_framework import viewsets, permissions, status
from django.http import HttpResponse
from .models import *
from .serializers import *
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Sum
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from datetime import timedelta
import csv


class ExpenseIncomeAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date for the filter", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date for the filter", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ]
    )
    def get(self, request, format=None):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        expenses = Expense.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).values('date', 'category__name').annotate(total=Sum('amount')).order_by('date')

        incomes = Income.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).values('date', 'category__name').annotate(total=Sum('amount')).order_by('date')

        data = {
            'expenses': list(expenses),
            'incomes': list(incomes)
        }

        return Response(data)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if Wallet.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("You already have a wallet.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, wallet=self.request.user.wallet)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user, wallet=self.request.user.wallet)


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, wallet=self.request.user.wallet)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user, wallet=self.request.user.wallet)


class FinanceViewSet(viewsets.ModelViewSet):
    queryset = Finance.objects.all()
    serializer_class = FinanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Finance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class ReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        date_from_str = request.query_params.get('date_from')
        date_to_str = request.query_params.get('date_to')

        try:
            if date_from_str:
                date_from = parse_date(date_from_str)
            else:
                date_from = None
            
            if date_to_str:
                date_to = parse_date(date_to_str)
                date_to = date_to + timedelta(days=1)
            else:
                date_to = None

            user = request.user
            if date_from and date_to:
                expenses = Expense.objects.filter(user=user, date__range=[date_from, date_to])
                incomes = Income.objects.filter(user=user, date__range=[date_from, date_to])
            elif date_from:
                expenses = Expense.objects.filter(user=user, date__gte=date_from)
                incomes = Income.objects.filter(user=user, date__gte=date_from)
            elif date_to:
                expenses = Expense.objects.filter(user=user, date__lt=date_to)
                incomes = Income.objects.filter(user=user, date__lt=date_to)
            else:
                expenses = Expense.objects.filter(user=user)
                incomes = Income.objects.filter(user=user)

            expense_serializer = ReportExpenseSerializer(expenses, many=True)
            income_serializer = ReportIncomeSerializer(incomes, many=True)

            combined_data = []
            combined_data.extend(expense_serializer.data)
            combined_data.extend(income_serializer.data)            
            return Response(combined_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CSVReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        date_from_str = request.query_params.get('date_from')
        date_to_str = request.query_params.get('date_to')

        try:
            if date_from_str:
                date_from = parse_date(date_from_str)
            else:
                date_from = None
            
            if date_to_str:
                date_to = parse_date(date_to_str)
                date_to = date_to + timedelta(days=1)
            else:
                date_to = None

            user = request.user
            if date_from and date_to:
                expenses = Expense.objects.filter(user=user, date__range=[date_from, date_to])
                incomes = Income.objects.filter(user=user, date__range=[date_from, date_to])
            elif date_from:
                expenses = Expense.objects.filter(user=user, date__gte=date_from)
                incomes = Income.objects.filter(user=user, date__gte=date_from)
            elif date_to:
                expenses = Expense.objects.filter(user=user, date__lt=date_to)
                incomes = Income.objects.filter(user=user, date__lt=date_to)
            else:
                expenses = Expense.objects.filter(user=user)
                incomes = Income.objects.filter(user=user)

            expense_serializer = ReportExpenseSerializer(expenses, many=True)
            income_serializer = ReportIncomeSerializer(incomes, many=True)

            report_data = []
            report_data.extend(expense_serializer.data)
            report_data.extend(income_serializer.data)
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="report.csv"'

            writer = csv.DictWriter(response, fieldnames=['id', 'amount', 'date', 'comments', 'username', 'balance', 'category', 'transaction_type'])
            writer.writeheader()
            writer.writerows(report_data)

            return response
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
