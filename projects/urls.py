from django.urls import path

from django.views.generic.base import RedirectView

from . import views

app_name = "projects"

urlpatterns = [
    path('<uuid:tenant_id>/projects/', views.ProjectList.as_view(), name='project-list'),
    path('<uuid:tenant_id>/projects/<uuid:pk>/', views.ProjectDetail.as_view(), name='project-detail'),
    path('<uuid:tenant_id>/projects/create/', views.ProjectCreate.as_view(), name='project-create'),
    path('<uuid:tenant_id>/projects/<uuid:pk>/delete/', views.ProjectDelete.as_view(), name='project-delete'),
    path('<uuid:tenant_id>/projects/<uuid:pk>/update/', views.ProjectUpdate.as_view(), name='project-update'),

]
