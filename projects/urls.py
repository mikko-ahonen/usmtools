from django.urls import path

from django.views.generic.base import RedirectView

from . import views

app_name = "projects"

urlpatterns = [
    path('<uuid:tenant_id>/', views.ProjectList.as_view(), name='project-list'),
    path('<uuid:tenant_id>/<uuid:pk>/', views.ProjectDetail.as_view(), name='project-detail'),
    #path('<uuid:tenant_id>/<uuid:pk>/dashboard/', views.ProjectDashboard.as_view(), name='project-dashboard'),
    path('<uuid:tenant_id>/<uuid:pk>/roadmap/', views.ProjectRoadmap.as_view(), name='project-roadmap'),
    path('<uuid:tenant_id>/<uuid:pk>/backlog/', views.ProjectBacklog.as_view(), name='project-backlog'),
    path('<uuid:tenant_id>/<uuid:pk>/sprints/', views.ProjectSprints.as_view(), name='project-sprints'),
    path('<uuid:tenant_id>/<uuid:pk>/teams/<uuid:team_id>/sprint/', views.ProjectSprint.as_view(), name='project-sprint'),
    path('<uuid:tenant_id>/<uuid:pk>/reports/', views.ProjectReports.as_view(), name='project-reports'),
    path('<uuid:tenant_id>/create/', views.ProjectCreate.as_view(), name='project-create'),
    path('<uuid:tenant_id>/<uuid:pk>/delete/', views.ProjectDelete.as_view(), name='project-delete'),
    path('<uuid:tenant_id>/<uuid:pk>/update/', views.ProjectUpdate.as_view(), name='project-update'),

]
