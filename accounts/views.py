import logging

from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, DeleteView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as OrigLoginView, PasswordResetView as OrigPasswordResetView, PasswordResetConfirmView as OrigPasswordResetConfirmView, PasswordChangeView as OrigPasswordChangeView, PasswordChangeDoneView as OrigPasswordChangeDoneView, LogoutView as OrigLogoutView
from django.utils import translation
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.validators import validate_email
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from registration.backends.default.views import RegistrationView as OrigRegistrationView
from registration.backends.default.views import ActivationView as OrigActivationView
from registration.backends.default.views import ResendActivationView as OrigResendActivationView

from workflows.models import Account
from .forms import LoginForm, PasswordResetForm, PasswordChangeForm, PasswordResetConfirmForm, JoinWaitingListForm

#from django.shortcuts import render
#from django.views.generic import ListView
#from django.shortcuts import get_object_or_404
#from django.urls import reverse_lazy

from .models import WaitingListEntry, WaitingListInvite, Invitation

logger = logging.getLogger(__name__)

class SuperUserOrSelfMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Logged in user is either superuser or the same user as the one passed as url argument 'user'
    """
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.username == self.kwargs['user']

class IndexView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return reverse_lazy('groups:list')
        return reverse_lazy('accounts:auth_login')


class LogoutView(OrigLogoutView):
    template_name = 'accounts/logout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'deleted' in self.kwargs:
            context['deleted'] = self.kwargs['deleted']
        else:
            context['deleted'] = False
        return context


class AccountDeleteView(SuperUserOrSelfMixin, DeleteView):
    template_name = 'accounts/delete.html'
    model = Account

    def get_object(self, queryset=None):
        username = self.kwargs['user']
        obj = get_object_or_404(Account, username=username)
        return obj

    def get_success_url(self):
        return reverse_lazy('accounts:deleted')

class JoinWaitingListView(CreateView):
    model = WaitingListEntry
    template_name = 'accounts/join_waiting_list_form.html'
    form_class = JoinWaitingListForm
    invite = None

    def dispatch(self, request, *args, **kwargs):
        if 'email' in kwargs:
            email = kwargs['email']
            try:
                validate_email(email)
            except ValidationError as e:
                raise SuspiciousOperation("Spam bot suspected: ", e)
            self.invite = WaitingListInvite.objects.filter(email=email).first()
        if self.invite is None and (not 'spam' in request.session or request.session['spam'] != 'no'):
            raise SuspiciousOperation("Spam bot suspected")
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invite'] = self.invite
        return context

    def form_valid(self, form):

        current_site = get_current_site(self.request)

        with transaction.atomic():
            self.object = form.save()

            for e in form.cleaned_data['invite_emails']:

                if (not Account.objects.filter(email=e).exists() and
                    not WaitingListEntry.objects.filter(email=e).exists() and
                    not WaitingListInvite.objects.filter(email=e).exists()):

                    logger.info("Adding invite for " + e)
                    i = WaitingListInvite(email=e, entry=self.object)
                    i.save()
                    logger.info("Invite " + str(id(i)))
            
                    transaction.on_commit(
                        lambda i=i: i.send_invitation_email(current_site, self.request)
                    )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('accounts:join-waiting-list-complete')

class LoginView(OrigLoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        request.session["spam"] = "no" # set session variable, which is checked at join waiting list
        return response

class PasswordResetView(OrigPasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    form_class = PasswordResetForm

class PasswordChangeView(LoginRequiredMixin, OrigPasswordChangeView):
    template_name = 'accounts/password_change_form.html'
    form_class = PasswordChangeForm

class PasswordChangeDoneView(LoginRequiredMixin, OrigPasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'

class PasswordResetConfirmViewOld(OrigPasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm


class PasswordResetConfirmView(OrigPasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm

class ActivationCompleteView(TemplateView):
    template_name='accounts/activation_complete.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['username'] = self.kwargs['user']
        return context

class RegistrationView(OrigRegistrationView):
    template_name = 'accounts/registration_form.html'
    lang = None
    invitation = None
    disallowed_url = 'accounts:registration_disallowed'

    def setup(self, request, *args, **kwargs):

        super().setup(request, *args, **kwargs)

        invitation_key = kwargs['invitation_key']
        try:
            self.invitation = Invitation.objects.get(key=invitation_key)
        except Invitation.DoesNotExist:
            pass


    def registration_allowed(self):
        if self.invitation is None:
            return False
        if not self.invitation.active:
            return False

        return True


    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.lang:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, self.lang)
        return response

    def get_success_url(self, user):
        return reverse_lazy('accounts:registration_complete')

    def register(self, form):
        account = None
        if self.request.user:
            try:
                account = Account.objects.get(username=self.request.user)
            except Account.DoesNotExist:
                pass
        if not account:
            account = super().register(form)
            account.invitation = self.invitation
            account.save()
        self.lang = account.lang
        return account


class ActivationView(OrigActivationView):
    template_name = 'accounts/registration_form.html'

    def get_success_url(self, user):
        return reverse_lazy('accounts:registration_activation_complete', kwargs={'user': user.username})


class ResendActivationView(OrigResendActivationView):
    template_name = 'accounts/resend_activation_form.html'

