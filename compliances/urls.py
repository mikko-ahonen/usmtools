from django.urls import path

from django.views.generic.base import RedirectView

from . import views

app_name = "compliances"

urlpatterns = [
    path('<uuid:tenant_id>/domains/', views.DomainList.as_view(), name='domain-list'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/dashboard/', views.DomainDashboard.as_view(), name='domain-dashboard'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/spec/', views.DomainSpec.as_view(), name='domain-spec'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/constraints/', views.DomainConstraints.as_view(), name='domain-constraints'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/projects/create/', views.DomainCreateProject.as_view(), name='domain-create-project'),
    path('<uuid:tenant_id>/domains/<uuid:domain_id>/projects/<uuid:pk>/setup/', views.DomainProjectSetup.as_view(), name='domain-project-setup'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/projects/<uuid:project_id>/roadmaps/create/', views.DomainProjectCreateRoadmap.as_view(), name='domain-project-create-roadmap'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/projects/<uuid:project_id>/backlogs/create/', views.DomainProjectCreateBacklog.as_view(), name='domain-project-create-backlog'),
    #path('<uuid:tenant_id>/domains/<uuid:pk>/projects/<uuid:project_id>/targets/<uuid:target_id>/audit/', views.DomainProjectTargetAudit.as_view(), name='domain-target-audit'),
    path("<uuid:tenant_id>/projects/<uuid:pk>/create-target/", views.create_target_for_project, name="project-create-target"),
    path("<uuid:tenant_id>/projects/<uuid:pk>/create-team/", views.create_team_for_project, name="project-create-team"),
    path("<uuid:tenant_id>/targets/<uuid:target_id>/<uuid:section_id>/select/", views.target_section_select, name="target-section-select"),
    path("<uuid:tenant_id>/teams/<uuid:team_id>/<uuid:category_id>/select/", views.team_category_select, name="team-category-select"),
    path("<uuid:tenant_id>/projects/<uuid:pk>/targets/<uuid:target_id>/delete/", views.delete_target, name="target-delete"),
    path("<uuid:tenant_id>/projects/<uuid:pk>/teams/<uuid:team_id>/delete/", views.delete_team, name="team-delete"),
]
