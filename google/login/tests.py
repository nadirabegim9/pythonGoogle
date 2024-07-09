from django.test import TestCase
from .models import CustomUser, Finance

class FinancialGoalTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.goal = Finance.objects.create(
            user=self.user, name='Test Goal', target_amount=1000, start_date=now().date(), end_date=now().date() + timedelta(days=30)
        )

    def test_goal_creation(self):
        self.assertEqual(self.goal.name, 'Test Goal')
        self.assertEqual(self.goal.target_amount, 1000)
        self.assertFalse(self.goal.is_achieved)
