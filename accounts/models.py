import os
import uuid
import logging

from django.forms import HiddenInput
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import format_lazy
from django.utils.translation import pgettext_lazy, gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.defaultfilters import filesizeformat

from multiselectfield import MultiSelectField
from registration.models import get_from_email

logger = logging.getLogger(__name__)

class Invitation(models.Model):
    title = models.CharField(max_length=255)
    key = models.UUIDField(default=uuid.uuid4)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} / {self.key}" + (" [ not active ]" if not self.active else "")


class WaitingListEntry(models.Model):
    email = models.EmailField(verbose_name=_('Email address'))
    why = models.TextField(verbose_name=_('Why do you want to use this service?'))
    source = models.TextField(verbose_name=_('Where did you hear about this service?'))
    interested_groups = models.TextField(verbose_name=_('Are you member of a groups that might have people interested in participating in Lovezone?'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Waiting list entry'
        verbose_name_plural = 'Waiting list entries'


class WaitingListInvite(models.Model):
    email = models.EmailField(verbose_name=_('Email address'))
    entry = models.ForeignKey(WaitingListEntry, on_delete=models.CASCADE, related_name='recommendations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email + ' / ' + self.entry.email

    def send_invitation_email(self, site, request=None):

        logger.info("Processing invite " + str(id(self)))
        logger.info("Sending invitation email to " + self.email)

        email_subject = 'accounts/invitation_email_subject.txt'
        email_body = 'accounts/invitation_email.txt'
        email_body_html = 'accounts/invitation_email.html'

        ctx_dict = {
            'site': site,
            'invitation': self,
            'request': request,
            'sender_email': self.entry.email,
        }

        subject = render_to_string(email_subject, ctx_dict, request=request)
        # Email subject *MUST NOT* contain newlines
        subject = ''.join(subject.splitlines())

        from_email = get_from_email(site)
        message_txt = render_to_string(email_body, ctx_dict, request=request)

        email_message = EmailMultiAlternatives(subject, message_txt, from_email, [self.email])

        if getattr(settings, 'REGISTRATION_EMAIL_HTML', True):
            try:
                message_html = render_to_string(email_body_html, ctx_dict, request=request)
            except TemplateDoesNotExist:
                pass
            else:
                email_message.attach_alternative(message_html, 'text/html')

        email_message.send()

    class Meta:
        verbose_name = 'Waiting list invite'
        verbose_name_plural = 'Waiting list invites'

