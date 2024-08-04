from django.urls import path

from django.views.generic.base import RedirectView

from . import views

app_name = "compliances"

urlpatterns = [
    path('<uuid:tenant_id>/domains/', views.DomainList.as_view(), name='domain-list'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/', views.DomainDetail.as_view(), name='domain-detail'),
]
