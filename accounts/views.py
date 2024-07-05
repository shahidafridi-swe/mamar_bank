from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import FormView
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import login, update_session_auth_hash

from django.urls import reverse_lazy
from django.views import View
from .forms import CustomUserCreationForm, UserUpdateForm
from django.contrib import messages
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

class UserRegistrationView(FormView):
    template_name = 'accounts/user_register.html'
    success_url = reverse_lazy('home')
    form_class = CustomUserCreationForm
    
    def form_valid(self, form):
        user = form.save()
        login(self.request,user)
        messages.success(self.request, f"Account created successfully !!! ")
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')

            
            

class UserBankAccountUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})
    
    

def changePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password Changed Successfully!!!")
            email_messages = render_to_string('accounts/change_password_email.html', {
                'user' : request.user,
            })
            send_email = EmailMultiAlternatives('Changed Password', '', to=[request.user.email])
            send_email.attach_alternative(email_messages, 'text/html')
            send_email.send()
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/change_password_form.html',{'form':form, 'type':'Change Password'})

