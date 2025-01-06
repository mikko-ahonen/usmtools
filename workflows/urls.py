from django.urls import path,register_converter

from django.views.generic.base import RedirectView

from . import views
from .converters import ResponsibilityTypesConverter

app_name = "workflows"

register_converter(ResponsibilityTypesConverter, 'responsibility_types')

urlpatterns = [
    path('', RedirectView.as_view(url='/workflows/tenants/')),
    path('tenants/', views.TenantList.as_view(), name='tenant-list'),
    path('tenants/create/', views.TenantCreate.as_view(), name='tenant-create'),
    path('<uuid:pk>/update/', views.TenantUpdate.as_view(), name='tenant-update'),
    path('<uuid:pk>/delete/', views.TenantDelete.as_view(), name='tenant-delete'),
    path('<uuid:tenant_id>/export/', views.TenantExport.as_view(), name='tenant-export'),
    path('<uuid:tenant_id>/organization-units/', views.OrganizationUnitList.as_view(), name='organization-unit-list'),
    path('<uuid:tenant_id>/organization-units/create/', views.OrganizationUnitCreate.as_view(), name='organization-unit-create'),
    path('<uuid:tenant_id>/organization-units/<uuid:pk>/delete/', views.OrganizationUnitDelete.as_view(), name='organization-unit-delete'),
    path('<uuid:tenant_id>/organization-units/<uuid:pk>/update/', views.OrganizationUnitUpdate.as_view(), name='organization-unit-update'),
    #path('<uuid:tenant_id>/shares/', views.ShareList.as_view(), name='share-list'),
    #path('<uuid:tenant_id>/shares/create/', views.ShareCreate.as_view(), name='share-create'),
    #path('<uuid:tenant_id>/shares/<uuid:pk>/delete/', views.ShareDelete.as_view(), name='share-delete'),
    path('<uuid:tenant_id>/services/<uuid:pk>/workflows/create/', views.WorkflowCreate.as_view(), name='workflow-create'),
    path('<uuid:tenant_id>/services/', views.ServiceList.as_view(), name='service-list'),
    path('<uuid:tenant_id>/services/create/', views.ServiceCreate.as_view(), name='service-create'),
    path('<uuid:tenant_id>/services/<uuid:pk>/delete/', views.ServiceDelete.as_view(), name='service-delete'),
    path('<uuid:tenant_id>/services/<uuid:pk>/update/', views.ServiceUpdate.as_view(), name='service-update'),
    path('<uuid:tenant_id>/services/<uuid:pk>/', views.ServiceDetail.as_view(), name='service-detail'),
    path('<uuid:tenant_id>/services/<uuid:pk>/customers/add/', views.ServiceCustomerAdd.as_view(), name='service-customer-add'),
    path('<uuid:tenant_id>/service-customers/<uuid:pk>/remove/', views.ServiceCustomerRemove.as_view(), name='service-customer-remove'),
    path('<uuid:tenant_id>/profiles/', views.ProfileList.as_view(), name='profile-list'),
    path('<uuid:tenant_id>/profiles/create/', views.ProfileCreate.as_view(), name='profile-create'),
    path('<uuid:tenant_id>/profiles/<uuid:pk>/delete/', views.ProfileDelete.as_view(), name='profile-delete'),
    path('<uuid:tenant_id>/profiles/<uuid:pk>/update/', views.ProfileUpdate.as_view(), name='profile-update'),
    path('<uuid:tenant_id>/profiles/<uuid:pk>/up/', views.ProfileUp.as_view(), name='profile-up'),
    path('<uuid:tenant_id>/profiles/<uuid:pk>/down/', views.ProfileDown.as_view(), name='profile-down'),
    path('<uuid:tenant_id>/customers/', views.CustomerList.as_view(), name='customer-list'),
    path('<uuid:tenant_id>/customers/create/', views.CustomerCreate.as_view(), name='customer-create'),
    path('<uuid:tenant_id>/customers/<uuid:pk>/delete/', views.CustomerDelete.as_view(), name='customer-delete'),
    path('<uuid:tenant_id>/customers/<uuid:pk>/update/', views.CustomerUpdate.as_view(), name='customer-update'),
    path('<uuid:tenant_id>/workflows/<uuid:pk>/', views.WorkflowDetail.as_view(), name='workflow-detail'),
    path('<uuid:tenant_id>/workflows/<uuid:pk>/delete/', views.WorkflowDelete.as_view(), name='workflow-delete'),
    path('<uuid:tenant_id>/workflows/<uuid:pk>/update/', views.WorkflowUpdate.as_view(), name='workflow-update'),
    path('<uuid:tenant_id>/steps/<uuid:pk>/activities/create/', views.ActivityCreate.as_view(), name='activity-create'),
    path('<uuid:tenant_id>/activities/<uuid:pk>/delete/', views.ActivityDelete.as_view(), name='activity-delete'),
    path('<uuid:tenant_id>/activities/<uuid:pk>/update/', views.ActivityUpdate.as_view(), name='activity-update'),
    path('<uuid:tenant_id>/activities/<uuid:pk>/up/', views.ActivityUp.as_view(), name='activity-up'),
    path('<uuid:tenant_id>/activities/<uuid:pk>/down/', views.ActivityDown.as_view(), name='activity-down'),
    path('<uuid:tenant_id>/activities/<uuid:pk>/responsibles/create/', views.ResponsibleCreateOrUpdate.as_view(), name='responsible-create'),
    path('<uuid:tenant_id>/responsibles/<uuid:pk>/delete/', views.ResponsibleDelete.as_view(), name='responsible-delete'),
    path('<uuid:tenant_id>/responsibles/<uuid:pk>/add-responsibilities/<str:types>/', views.ResponsibleAddResponsibilities.as_view(), name='responsible-add-responsibilities'),
    path('<uuid:tenant_id>/responsibles/<uuid:pk>/remove-responsibilities/<str:types>/', views.ResponsibleRemoveResponsibilities.as_view(), name='responsible-remove-responsibilities'),
    path('<uuid:tenant_id>/responsibles/<uuid:pk>/work-instructions/create/', views.WorkInstructionCreate.as_view(), name='work-instruction-create'),
    path('<uuid:tenant_id>/work-instructions/<uuid:pk>/delete/', views.WorkInstructionDelete.as_view(), name='work-instruction-delete'),
    path('<uuid:tenant_id>/work-instructions/<uuid:pk>/update/', views.WorkInstructionUpdate.as_view(), name='work-instruction-update'),
    #path('<uuid:tenant_id>/user/services/', views.UserServiceList.as_view(), name='user-service-list'),
    path('<uuid:tenant_id>/workflows/<uuid:pk>/printable/', views.WorkflowDetailPrintable.as_view(), name='workflow-detail-printable'),
    #path('<uuid:tenant_id>/shared/workflows/<uuid:pk>/<uuid:token1>/<uuid:token2>/', views.SharedWorkflowDetail.as_view(), name='shared-workflow-detail'),
    #path('<uuid:tenant_id>/profile/services/', views.ProfileServiceList.as_view(), name='profile-service-list'),
    #path('<uuid:tenant_id>/profile/workflows/<uuid:pk>/', views.ProfileWorkflowDetail.as_view(), name='profile-workflow-detail'),

]
