from django.urls import path,register_converter

from django.views.generic.base import RedirectView

from . import views

app_name = "xref"

urlpatterns = [
    path('', views.StandardList.as_view(), name='standard-list'),
    path('standards/', views.StandardList.as_view(), name='standard-list'),
    path('standards/<uuid:pk>/', views.StandardDetail.as_view(), name='standard-detail'),
    path('standards/create/', views.StandardCreate.as_view(), name='standard-create'),
    path('standards/<uuid:pk>/update/', views.StandardUpdate.as_view(), name='standard-update'),
    path('standards/<uuid:pk>/delete/', views.StandardDelete.as_view(), name='standard-delete'),
    path('standards/<uuid:pk>/controls/create/', views.ControlCreate.as_view(), name='control-create'),
    path('controls/<uuid:pk>/delete', views.ControlDelete.as_view(), name='control-delete'),
    path('controls/<uuid:pk>/update', views.ControlUpdate.as_view(), name='control-update'),
    path('controls/<uuid:pk>/', views.ControlDetail.as_view(), name='control-detail'),
    path('controls/<uuid:pk>/requirements/<uuid:requirement_id>/', views.RequirementDetail.as_view(), name='requirement-detail'),
    path('controls/<uuid:pk>/requirements/<uuid:requirement_id>/statements/<uuid:statement_id>/', views.StatementDetail.as_view(), name='statement-detail'),
    #path('controls/<uuid:pk>/requirements/<uuid:requirement_id>/statements/<uuid:statement_id>/tasks/<uuid:task_id>/', views.TaskDetail.as_view(), name='task-detail'),
    path('controls/<uuid:pk>/requirements/create/', views.RequirementCreate.as_view(), name='requirement-create'),
    path('requirements/<uuid:pk>/delete', views.RequirementDelete.as_view(), name='requirement-delete'),
    path('requirements/<uuid:pk>/update', views.RequirementUpdate.as_view(), name='requirement-update'),
    path('requirements/<uuid:pk>/statements/create/', views.StatementCreate.as_view(), name='statement-create'),
    path('statements/<uuid:pk>/delete', views.StatementDelete.as_view(), name='statement-delete'),
    path('statements/<uuid:pk>/update', views.StatementUpdate.as_view(), name='statement-update'),
    path('statements/<uuid:pk>/tasks/create/', views.TaskCreate.as_view(), name='task-create'),
    path('statements/<uuid:statement_id>/tasks/<uuid:pk>/delete', views.TaskDelete.as_view(), name='task-delete'),
    path('statements/<uuid:statement_id>/tasks/<uuid:pk>/update', views.TaskUpdate.as_view(), name='task-update'),
]
