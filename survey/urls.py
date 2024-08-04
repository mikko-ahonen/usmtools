from django.urls import path,register_converter

from django.views.generic.base import RedirectView

from . import views

app_name = "survey"

urlpatterns = [
    path('usm-survey/', views.USMSurveyWelcome.as_view(), name='usm-survey-welcome'),
    path('usm-survey/generate-invitation-link/', views.USMSurveyGenerateInvitationLink.as_view(), name='usm-survey-generate-invitation-link'),
    path('usm-survey/show-invitation-link/<str:link>/', views.USMSurveyShowInvitationLink.as_view(), name='usm-survey-show-invitation-link'),
    path('usm-survey/leads/', views.LeadList.as_view(), name='lead-list'),
    path('usm-survey/leads/<uuid:pk>/reject', views.FreeView.as_view(), name='lead-reject'),
    path('usm-survey/leads/<uuid:pk>/free', views.FreeView.as_view(), name='lead-free'),
    path('usm-survey/leads/<uuid:pk>/claim', views.ClaimView.as_view(), name='lead-claim'),
    path('usm-survey/leads/<uuid:pk>/mark/<str:category>/', views.MarkView.as_view(), name='lead-mark'),
    path('usm-survey/survey/', views.USMSurveyView.as_view(), name='usm-survey'),
    path('usm-survey/survey/<str:link>/', views.USMSurveyView.as_view(), name='usm-survey-by-invitation'),
    path('usm-survey/qualify/', views.USMSurveyQualify.as_view(), name='usm-survey-qualify'),
    path('usm-survey/qualify/<uuid:pk>/thank-you', views.USMSurveyQualifyThankYou.as_view(), name='usm-survey-qualify-thank-you'),
    path('usm-survey/<uuid:pk>/background/', views.USMSurveyBackground.as_view(), name='usm-survey-background'),
    path('usm-survey/<uuid:pk>/thank-you/', views.USMSurveyThankYou.as_view(), name='usm-survey-thank-you'),
    path('usm-survey/<uuid:pk>/report/', views.USMSurveyReport.as_view(), name='usm-survey-report'),
    path('usm-survey/<uuid:pk>/diagram/<str:highlight>/', views.USMSurveyDiagram.as_view(), name='usm-survey-diagram'),
    path('usm-survey/<uuid:pk>/diagram/', views.USMSurveyDiagram.as_view(), name='usm-survey-diagram'),
    path('usm-survey/invited/<str:link>/', views.USMSurveyWelcome.as_view(), name='usm-survey-welcome-by-invitation'),
]
