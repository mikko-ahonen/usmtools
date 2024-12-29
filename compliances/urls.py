from django.urls import path

from django.views.generic.base import RedirectView

from . import views

app_name = "compliances"

urlpatterns = [
    path('<uuid:tenant_id>/domains/', views.DomainList.as_view(), name='domain-list'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/', views.DomainDetail.as_view(), name='domain-detail'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/spec/', views.DomainSpec.as_view(), name='domain-spec'),
    #path('<uuid:tenant_id>/domains/<uuid:pk>/deployment/', views.DeploymentBoard.as_view(), name='deployment-board'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/projects/create/', views.DomainCreateProject.as_view(), name='domain-create-project'),
    path('<uuid:tenant_id>/domains/<uuid:domain_id>/projects/<uuid:pk>/setup/', views.DomainProjectSetup.as_view(), name='domain-project-setup'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/projects/<uuid:project_id>/roadmaps/create/', views.DomainProjectCreateRoadmap.as_view(), name='domain-project-create-roadmap'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/projects/<uuid:project_id>/targets/<uuid:target_id>/audit/', views.DomainProjectTargetAudit.as_view(), name='domain-target-audit'),
    path("<uuid:tenant_id>/projects/<uuid:pk>/create-target/", views.create_target_for_project, name="project-create-target"),
    path("<uuid:tenant_id>/targets/<uuid:target_id>/<uuid:section_id>/", views.target_section_select, name="target-section-select"),
]
