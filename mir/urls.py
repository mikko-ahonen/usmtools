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
]
