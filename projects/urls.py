from django.urls import path

from django.views.generic.base import RedirectView

from . import views

app_name = "projects"

urlpatterns = [
    path('<uuid:tenant_id>/projects/', views.ProjectList.as_view(), name='project-list'),
    path('<uuid:tenant_id>/projects/<uuid:pk>/', views.ProjectDetail.as_view(), name='project-detail'),
]
