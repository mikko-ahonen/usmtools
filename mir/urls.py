from django.urls import path

from django.views.generic.base import RedirectView

from . import views

app_name = "mir"

urlpatterns = [
    path('', views.EntityList.as_view(), name='entity-list'),
    path('trainings/', views.TrainingList.as_view(), name='training-list'),
    path('trainings/create/', views.TrainingCreate.as_view(), name='training-create'),
    path('trainings/<uuid:pk>/delete/', views.TrainingDelete.as_view(), name='training-delete'),
    path('trainings/<uuid:pk>/update/', views.TrainingUpdate.as_view(), name='training-update'),
    path('employees/', views.EmployeeList.as_view(), name='employee-list'),
    path('employees/create/', views.EmployeeCreate.as_view(), name='employee-create'),
    path('employees/<uuid:pk>/delete/', views.EmployeeDelete.as_view(), name='employee-delete'),
    path('employees/<uuid:pk>/update/', views.EmployeeUpdate.as_view(), name='employee-update'),
]
