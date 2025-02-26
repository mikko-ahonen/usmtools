from django.urls import path
from django.views.generic.base import RedirectView

from . import views

app_name = "public"

urlpatterns = [
    path('lang/<slug:lang>/', views.SetLangView.as_view(), name='set-lang'),
]
