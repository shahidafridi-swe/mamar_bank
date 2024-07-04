from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSACTION_TYPE
class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE)
    transaction_time = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-transaction_time']
