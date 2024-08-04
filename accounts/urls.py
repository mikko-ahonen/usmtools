from django.conf import settings
from django.conf.urls import include
from django.urls import re_path, path, register_converter
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from .converters import UsernameConverter
from .views import RegistrationView, ActivationView, ResendActivationView, LoginView, PasswordResetView, PasswordResetConfirmView, PasswordChangeView, PasswordChangeDoneView, JoinWaitingListView, ActivationCompleteView, AccountDeleteView, LogoutView

app_name = 'accounts'

register_converter(UsernameConverter, 'user')

urlpatterns = [
    path('<user:user>/activate/complete/', ActivationCompleteView.as_view(), name='registration_activation_complete'),
    path('activate/resend/', ResendActivationView.as_view(), name='registration_resend_activation'),
    #re_path(r'^join-waiting-list/((?P<email>[^/]+)/)?$', JoinWaitingListView.as_view(), name='join-waiting-list'),
    #path('join-waiting-list/complete', TemplateView.as_view(template_name='accounts/join_waiting_list_complete.html'), name='join-waiting-list-complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    path('activate/<activation_key>/', ActivationView.as_view(), name='registration_activate'),
    path('register/complete/', TemplateView.as_view(template_name='accounts/registration_complete.html'), name='registration_complete'),
    path('register/closed/', TemplateView.as_view(template_name='accounts/registration_closed.html'), name='registration_disallowed'),
    path('register/<invitation_key>/', RegistrationView.as_view(), name='registration_register'),

    path('login/', LoginView.as_view(), name='auth_login'),
    path('logout/', LogoutView.as_view(), {'deleted': False}, name='auth_logout'),
    path('deleted/', LogoutView.as_view(), {'deleted': True}, name='deleted'),
    path('delete/<user:user>/', AccountDeleteView.as_view(), name='delete'),
    path('password/change/', PasswordChangeView.as_view(success_url=reverse_lazy('accounts:auth_password_change_done')), name='auth_password_change'),
    path('password/change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='auth_password_change_done'),
    path('password/reset/', PasswordResetView.as_view( success_url=reverse_lazy('accounts:auth_password_reset_done')), name='auth_password_reset'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='auth_password_reset_complete'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='auth_password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view( success_url=reverse_lazy('accounts:auth_password_reset_complete')), name='auth_password_reset_confirm'),
]
