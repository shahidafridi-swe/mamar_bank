from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from .forms import DepositForm, WithdrawForm, LoanRequestForm, TransferForm
from .models import Transaction
from accounts.models import UserBankAccount
from core.models import Bank
from .constants import DEPOSIT, WITHDRAW, LOAN_REQUEST, LOAN_PAY, TRANSFER_MONEY, RECIEVED_MONEY
from django.urls import reverse_lazy

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

def send_trnasaction_email(user, amount, subject, template):
    messages = render_to_string(template, {
        'user' : user,
        'amount' : amount,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(messages, 'text/html')
    send_email.send()

class TransactionCreateMixin(CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    success_url = reverse_lazy('report')
    title = ''
    
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context

class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'
    
    def get_initial(self):
        initial = {'transaction_type' : DEPOSIT}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        
        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f"{amount} BDT has deposited successfull in your account!")
        send_trnasaction_email(self.request.user, amount,"Deposit Message", 'transactions/deposit_email.html')
        return super().form_valid(form)
    

class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'
    
    def get_initial(self):
        initial = {'transaction_type' : WITHDRAW}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        bank = Bank.objects.get(name="Mamar Bank")
        account = self.request.user.account
        if bank.is_bankrupt == False:
            account.balance -= amount
            account.save(
                update_fields = ['balance']
            )
            send_trnasaction_email(self.request.user, amount,"Withdraw Message", 'transactions/withdraw_email.html')
            messages.success(self.request, f"{amount} BDT has withdrawn successfull from your account!")
            
        else:
            messages.error(self.request, f"Sorry, The Bank is bankrupt now. \nYou can't withdraw money at this moment.")
            return redirect('withdraw')
            
        return super().form_valid(form)
    

class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Loan Request'
    
    def get_initial(self):
        initial = {'transaction_type' : LOAN_REQUEST}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(account = self.request.user.account, transaction_type = LOAN_REQUEST, loan_approve = True).count()
        
        if current_loan_count >= 3:
            return HttpResponse("Already you have taken loan for two times, You can't take more loan at this moment!!!")
        send_trnasaction_email(self.request.user, amount,"Loan Request Message", 'transactions/loan_request_email.html')
        messages.success(self.request, f"{amount} BDT loan request has successfull from your account to admin!")
        return super().form_valid(form)
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account = self.request.user.account
        )
        
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            queryset = queryset.filter(transaction_time__date__gte = start_date,transaction_time__date__lte=end_date )
            
            self.balance = Transaction.objects.filter(transaction_time__date__gte = start_date, transaction_time__date__lte = end_date).aggregate(Sum('amount'))['amount__sum']
        
        else:
            self.balance = self.request.user.account.balance
            
        return queryset.distinct()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account' : self.request.user.account
        })
        return context
            
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        
        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAY
                loan.save()
                return redirect('loans')
            else:
                messages.error(self.request, f"You can't paid your loan, Your loan amount is greater then your account balance.")
                return redirect('loans')

class LoanListView(LoginRequiredMixin, ListView):
    template_name = 'transactions/loans.html'
    model = Transaction
    context_object_name = 'loans'
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account, transaction_type = LOAN_REQUEST)
        return queryset
    

class TransferMoneyView(TransactionCreateMixin):
    form_class = TransferForm  
    title = 'Transfer Money'
    
    def get_initial(self):
        initial = {'transaction_type':TRANSFER_MONEY}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        transfered_account_number = form.cleaned_data.get('transfered_account_number')
        account = self.request.user.account
        transfered_account = None
        
        try:
            transfered_account = UserBankAccount.objects.get(account_number=transfered_account_number)
        except UserBankAccount.DoesNotExist:
            messages.error(self.request, "Sorry, the given account number is not found!")
            return redirect('transfer_money')
        
        if transfered_account:
            account.balance -= amount
            transfered_account.balance += amount
            account.save(update_fields=['balance'])
            transfered_account.save(update_fields=['balance'])
            send_trnasaction_email(self.request.user, amount,"Transfered Money", 'transactions/transfer_money_email.html')
            send_trnasaction_email(transfered_account.user, amount,"Recieved Money", 'transactions/recieve_money_email.html')
            messages.success(self.request, f"{amount} BDT has been successfully transferred from your account to {transfered_account.account_number}!")
        else:
            messages.error(self.request, "Sorry, the given account number is not found!")
            return redirect('transfer_money')
        return super().form_valid(form)
        
    def form_invalid(self, form):
        messages.error(self.request, "Form is invalid. Please correct the errors.")
        return super().form_invalid(form)