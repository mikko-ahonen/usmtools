from django.urls import path

from django.views.generic.base import RedirectView

from . import views

app_name = "mir"

urlpatterns = [
    path('<uuid:tenant_id>/trainings/', views.TrainingList.as_view(), name='training-list'),
    path('<uuid:tenant_id>/trainings/create/', views.TrainingCreate.as_view(), name='training-create'),
    path('<uuid:tenant_id>/trainings/<uuid:pk>/delete/', views.TrainingDelete.as_view(), name='training-delete'),
    path('<uuid:tenant_id>/trainings/<uuid:pk>/update/', views.TrainingUpdate.as_view(), name='training-update'),
    path('<uuid:tenant_id>/employees/', views.EmployeeList.as_view(), name='employee-list'),
    path('<uuid:tenant_id>/employees/create/', views.EmployeeCreate.as_view(), name='employee-create'),
    path('<uuid:tenant_id>/employees/<uuid:pk>/delete/', views.EmployeeDelete.as_view(), name='employee-delete'),
    path('<uuid:tenant_id>/employees/<uuid:pk>/update/', views.EmployeeUpdate.as_view(), name='employee-update'),
    path('<uuid:tenant_id>/documents/', views.DocumentList.as_view(), name='document-list'),
    path('<uuid:tenant_id>/documents/create/', views.DocumentCreate.as_view(), name='document-create'),
    path('<uuid:tenant_id>/documents/<uuid:pk>/delete/', views.DocumentDelete.as_view(), name='document-delete'),
    path('<uuid:tenant_id>/documents/<uuid:pk>/update/', views.DocumentUpdate.as_view(), name='document-update'),
    path('<uuid:tenant_id>/risks/', views.RiskList.as_view(), name='risk-list'),
    path('<uuid:tenant_id>/risks/create/', views.RiskCreate.as_view(), name='risk-create'),
    path('<uuid:tenant_id>/risks/<uuid:pk>/delete/', views.RiskDelete.as_view(), name='risk-delete'),
    path('<uuid:tenant_id>/risks/<uuid:pk>/update/', views.RiskUpdate.as_view(), name='risk-update'),
]
