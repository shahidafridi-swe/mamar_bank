from django.contrib import admin

# from transactions.models import Transaction
from .models import Transaction
from .views import send_trnasaction_email

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approve']
    
    def save_model(self, request, obj, form, change):
        if obj.loan_approve ==True:    
            obj.account.balance += obj.amount
            obj.balance_after_transaction = obj.account.balance
            obj.account.save()
            send_trnasaction_email(obj.account.user, obj.amount,"Loan Approval Message", 'transactions/loan_approval_email.html')
            
        super().save_model(request, obj, form, change)
