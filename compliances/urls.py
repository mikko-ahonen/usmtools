from django.urls import path

from django.views.generic.base import RedirectView

from . import views

app_name = "compliances"

urlpatterns = [
    path('<uuid:tenant_id>/domains/', views.DomainList.as_view(), name='domain-list'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/', views.DomainDetail.as_view(), name='domain-detail'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/deployment/', views.DeploymentBoard.as_view(), name='deployment-board'),
    path("<uuid:tenant_id>/targets/<uuid:target_id>/<uuid:section_id>/", views.target_section_select, name="target-section-select"),
    path('<uuid:tenant_id>/projects/<uuid:pk>/roadmaps/create/', views.ProjectRoadmapCreate.as_view(), name='project-roadmap-create'),
    path('<uuid:tenant_id>/projects/<uuid:pk>/setup/', views.ProjectSetup.as_view(), name='project-setup'),
    path("<uuid:tenant_id>/projects/<uuid:pk>/create-target", views.create_target_for_project, name="project-create-target"),
]
