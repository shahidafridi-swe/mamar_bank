from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.DepositMoneyView.as_view(), name='deposit'),
    path('withdraw/', views.WithdrawMoneyView.as_view(), name='withdraw'),
    path('transfer_money/', views.TransferMoneyView.as_view(), name='transfer_money'),
    path('report/', views.TransactionReportView.as_view(), name='report'),
    path('loan_request/', views.LoanRequestView.as_view(), name='loan_request'),
    path('lonas/', views.LoanListView.as_view(), name='loans'),
    path('loan_pay/<int:loan_id>/', views.PayLoanView.as_view(), name='loan_pay'),
]
