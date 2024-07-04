from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']
        
    def __init__(self, *args, **kwargs):
        self.user_account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()
        
        
    def save(self, commit=False):
        self.instance.account = self.user_account
        self.instance.balance_after_transaction = self.user_account.balance
        return super().save()
    
    
class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f"You need to deposit at least {min_deposit_amount} BDT"
            )
        return amount

class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.user_account
        min_withdraw_amount = 500
        max_withdraw_amount = 25000
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        
        if amount<min_withdraw_amount:
            raise forms.ValidationError(
                f"You need to withdraw at least {min_withdraw_amount} BDT"
            )
        elif amount > max_withdraw_amount:
            raise forms.ValidationError(
                f"You can withdraw at most {max_withdraw_amount} BDT"
            )
        elif amount > balance:
            raise forms.ValidationError(
                f"You have {balance} BDT, in your account. \nYou can't withdraw more than your account balance."
            )
        
        return amount
    
    
class TransferForm(TransactionForm):
    transfered_account_number = forms.IntegerField()
    
    class Meta:
        model = Transaction
        fields = ['transaction_type','transfered_account_number', 'amount']
    def clean_amount(self):
        account = self.user_account
        min_transfer_amount = 100
        max_transfer_amount = 100000
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        if min_transfer_amount > amount :
            raise forms.ValidationError(
                f"You have to transfer at least {min_transfer_amount} BDT."
            )
        elif max_transfer_amount < amount :
            raise forms.ValidationError(
                f"You can't transfer more than {max_transfer_amount} BDT for a single time."
            )
        elif balance < amount :
            raise forms.ValidationError(
                f"You have {balance} BDT, in your account. \nYou can't transfer more than your account balance."
            )
        
        return amount

    
class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        return amount
        