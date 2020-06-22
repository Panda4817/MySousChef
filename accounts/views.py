from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, url_has_allowed_host_and_scheme
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.contrib.auth import login, authenticate, update_session_auth_hash, REDIRECT_FIELD_NAME, get_user_model, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordContextMixin
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail

from .signals import show_login_message, show_logout_message
from .forms import SignUpForm, ContactForm, ChangeUsernameForm, ChangeEmailForm
from .tokens import account_activation_token
from django.core.cache import cache


UserModel = get_user_model()

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('recipes:dashboard')
    else:
        return render(request, 'registration/index.html')

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            cache.clear()
            current_site = get_current_site(request)
            subject = 'Activate Your MySousChef Account'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            messages.info(
                request, "Please confirm your email address to complete the registration.")
            return redirect('accounts:index')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})


# When link in email is clicked, activation process occurs
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        cache.clear()
        login(request, user)
        messages.info(
            request, f"Hello { user.username }! Welcome to MySousChef")
        return redirect('recipes:dashboard')

    else:
        messages.error(
            request, "The confirmation link was invalid, possibly because it has already been used.")
        return redirect('accounts:index')

class myPasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            **(self.extra_context or {})
        })
        return context


class myPasswordResetView(myPasswordContextMixin, FormView):
    email_template_name = 'registration/password_reset_email.html'
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = 'registration/mypassword_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    template_name = 'registration/password_reset_form.html'
    title = _('Password reset')
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'


class myPasswordResetDoneView(myPasswordContextMixin, TemplateView):
    template_name = 'registration/password_reset_done.html'
    title = _('Password reset sent')


class myPasswordResetConfirmView(myPasswordContextMixin, FormView):
    form_class = SetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = 'set-password'
    success_url = reverse_lazy('accounts:password_reset_complete')
    template_name = 'registration/password_reset_confirm.html'
    title = _('Enter new password')
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Password reset unsuccessful'),
                'validlink': False,
            })
        return context




# When password reset  is completed successfully, redirects to login page
def password_reset_complete(request):
    messages.info(request, "Your password has been reset.")
    return redirect('accounts:login')


@login_required(login_url=reverse_lazy("accounts:login"))
def account(request):
    uform = ChangeUsernameForm()
    eform = ChangeEmailForm()
    context = {
        'uform': uform,
        'eform': eform,
    }
    return render(request, 'registration/account.html', context)

@login_required(login_url=reverse_lazy("accounts:login"))
def update_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk = request.user.id)
            user.username = form.cleaned_data['username']
            user.save()
            cache.clear()
            messages.success(request, "Username changed successfully!")
        return redirect('accounts:account')
    
    return redirect('accounts:account')

@login_required(login_url=reverse_lazy("accounts:login"))
def update_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk = request.user.id)
            user.email = form.cleaned_data['email']
            user.profile.email_confirmed = False
            user.save()
            cache.clear()
            current_site = get_current_site(request)
            subject = 'Email Changed - Activate Your MySousChef Account again'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            logout(request)            
            messages.info(
                request, "Please confirm your new email address to complete the registration process again.")
        return redirect('accounts:index')
    
    return redirect('accounts:account')

class myPasswordChangeView(myPasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_done')
    template_name = 'registration/password_change_form.html'
    title = _('Password change')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


# When password is changed sucessfully, redirects back to account page
@login_required(login_url=reverse_lazy("accounts:login"))
def password_change_done(request):
    messages.info(request, "Your password has been updated.")
    return redirect('accounts:account')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email = form.cleaned_data['email']
            cc_myself = form.cleaned_data['cc_myself']

            message_to_send = message + ' from ' + name
            recipients = [settings.EMAIL_HOST_USER]
            if cc_myself:
                recipients.append(email)

            send_mail(subject, message_to_send, email, recipients)
            messages.info(
                request, "Thank you for the message. We will get back to you as soon as possible.")
        if request.user.is_authenticated:
            return redirect('recipes:dashboard')
        else:
            return redirect('accounts:index')
    
    form = ContactForm()
    if request.user.is_authenticated:
        return render(request, 'recipes/contact.html', {'cform': form})
    else:
        return render(request, 'registration/contact.html', {'cform': form})