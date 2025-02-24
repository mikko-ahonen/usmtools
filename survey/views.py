import json
import logging
import plotly.graph_objects as go
import plotly.io as io

from django.utils.translation import gettext_lazy as _
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied

from django.contrib import messages

from . import forms
from .models import USMSurvey, Question, Lead
from workflows.models import Account
import base64
from urllib.parse import urlencode, quote_plus, parse_qs

logger = logging.getLogger(__name__)
    

class USMSurveyGenerateInvitationLink(LoginRequiredMixin, FormView):
    form_class = forms.USMGenerateInvitationForm
    template_name = 'survey/usm-survey-generate-invitation-link.html'

    def form_valid(self, form):
        data = dict(form.cleaned_data)
        data['invited_by'] = self.request.user.pk
        
        data_url = urlencode(data, quote_via=quote_plus)
        data_b64 = base64.b64encode(bytes(data_url, 'utf-8')).decode('utf-8')

        return HttpResponseRedirect(reverse_lazy('survey:usm-survey-show-invitation-link', kwargs={'link': data_b64}))


class USMSurveyShowInvitationLink(LoginRequiredMixin, TemplateView):
    template_name = 'survey/usm-survey-show-invitation-link.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        link = kwargs.get('link')
        context['link'] = f"{self.request.scheme}://{self.request.get_host()}" + reverse('survey:usm-survey-welcome-by-invitation', kwargs={'link': link})
        return context


class MarkView(LoginRequiredMixin, UpdateView):
    model = Lead
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        category = self.kwargs.pop('category')
        if self.object.category == category:
            raise ValueError("This should never happen")
        if self.object.status == Lead.STATUS_UNQUALIFIED and category != Lead.CATEGORY_REJETED:
            self.object.status = STATUS_FREE
        self.object.category = category
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('survey:lead-list'))


class FreeView(LoginRequiredMixin, UpdateView):
    model = Lead
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status = STATUS_FREE
        self.object.claimed_by = None
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('survey:lead-list'))


class ClaimView(LoginRequiredMixin, UpdateView):
    model = Lead
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status = STATUS_CLAIMED
        self.object.claimed_by = request.user
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('survey:lead-list'))


class RejectView(LoginRequiredMixin, UpdateView):
    model = Lead
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.category = CATEGORY_REJECTED
        self.object.status = STATUS_REJECTED
        self.object.claimed_by = None
        self.object.save()
        return HttpResponseRedirect(reverse_lazy('survey:lead-list'))

class LeadList(LoginRequiredMixin, ListView):
    model = Lead
    template_name = 'survey/lead-list.html'
    context_object_name = 'leads'


class USMSurveyWelcome(TemplateView):
    template_name = 'survey/usm-survey-welcome.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        link = kwargs.pop('link')
        if link:
            data_qs = base64.b64decode(bytes(link, 'utf-8')).decode('utf-8')
            data = parse_qs(data_qs)
            account = Account.objects.get(pk=data['invited_by'][0])
            context['link'] = link
            context['invited_by_name'] = account.get_full_name()
            context['invited_by_email'] = account.email
            context['invitee_name'] = data['invitee_name'][0]
            context['invitee_email'] = data['invitee_email'][0]
            context['invitee_org'] = data['invitee_org'][0]
            context['invitation_group'] = data['invitation_group'][0]
        return context


class USMSurveyQualify(CreateView):
    form_class = forms.USMQualifyForm
    model = Lead
    template_name = 'survey/usm-qualify.html'

    def get_success_url(self):
        return reverse_lazy('survey:usm-survey-qualify-thank-you', kwargs={'pk': self.object.id})

class USMSurveyQualifyThankYou(DetailView):
    template_name = 'survey/usm-survey-qualify-thank-you.html'
    model = Lead


class USMSurveyView(CreateView):
    form_class = forms.USMSurveyForm
    model = USMSurvey
    template_name = 'survey/usm-survey.html'

    def get_success_url(self):
        return reverse_lazy('survey:usm-survey-background', kwargs={'pk': self.object.id})


class USMSurveyBackground(UpdateView):
    form_class = forms.USMSurveyBackgroundForm
    model = USMSurvey
    template_name = 'survey/usm-survey-background.html'

    def get_success_url(self):
        return reverse_lazy('survey:usm-survey-thank-you', kwargs={'pk': self.object.id})


class USMSurveyThankYou(DetailView):
    template_name = 'survey/usm-survey-thank-you.html'
    model = USMSurvey


class USMSurveyReport(DetailView):
    model = USMSurvey
    template_name = 'survey/usm-survey-report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = [ f for f in USMSurvey._meta.get_fields() if isinstance(f, Question) ]
        return context


class USMSurveyDiagram(SingleObjectMixin, View):
    model = USMSurvey

    def get(self, request, pk, highlight=None):

        survey = self.get_object()

        fields = [ f for f in USMSurvey._meta.get_fields() if isinstance(f, Question) ]
        theta = [ f.verbose_name for f in fields ]
        text = [ f.verbose_name if f.name == highlight else " " for f in fields ]
        values_hl = [ getattr(survey, f.name) if f.name == highlight else None for f in fields ]
        values = [ getattr(survey, f.name) for f in fields ]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            mode="lines+markers",
            r=values + [values[0]],
            theta=theta,
            fill='toself',
            connectgaps=True,
        ))

        if highlight:
            fig.add_trace(go.Scatterpolar(
                mode="text+markers",
                r=values_hl,
                theta=theta,
                marker_size=15,
                marker_color="blue",
                text=text,
                textfont_size=20,
                textposition="bottom center",
                connectgaps=True,
            ))

        fig.update_layout(
          polar=dict(
            radialaxis=dict(
              visible=False,
              range=[0, 7]
            ),
            angularaxis_color="lightgray" if highlight else "black",
            angularaxis_layer="above traces",
            angularaxis_tickfont_size=15 if highlight else 18,
            #angularaxis_tickcolor="blue",
          ), 
          showlegend=False,
          #margin_t=100, 
          #margin_b=100,
          #margin_l=200,
          #margin_r=200,
          autosize=False,
          width=750,
          height=400,
        )


        img = io.to_image(fig, format='png')

        # <view logic>
        return HttpResponse(img, content_type="image/png")
