from django.urls import path,register_converter

from django.views.generic.base import RedirectView

from . import views

app_name = "xref"

urlpatterns = [
    path('', views.CrossReferenceList.as_view(), name='root'),
    path('cross-references/', views.CrossReferenceList.as_view(), name='cross-reference-list'),
    path('cross-references/<uuid:pk>/', views.CrossReferenceDetail.as_view(), name='cross-reference-detail'),
    path('cross-references/create/', views.CrossReferenceCreate.as_view(), name='cross-reference-create'),
    path('cross-references/<uuid:pk>/update/', views.CrossReferenceUpdate.as_view(), name='cross-reference-update'),
    path('cross-references/<uuid:pk>/delete/', views.CrossReferenceDelete.as_view(), name='cross-reference-delete'),
    path('cross-references/<uuid:cross_reference_id>/sections/create/', views.SectionCreate.as_view(), name='section-create'),
    path('sections/<uuid:pk>/create/', views.SectionCreate.as_view(), name='section-create-child'),
    path('sections/<uuid:pk>/delete/', views.SectionDelete.as_view(), name='section-delete'),
    path('sections/<uuid:pk>/update/', views.SectionUpdate.as_view(), name='section-update'),
    path('sections/<uuid:pk>/', views.SectionDetail.as_view(), name='section-detail'),
    path('sections/<uuid:pk>/requirements/<uuid:requirement_id>/', views.RequirementDetail.as_view(), name='requirement-detail'),
    path('sections/<uuid:pk>/requirements/<uuid:requirement_id>/statements/<uuid:statement_id>/', views.StatementDetail.as_view(), name='statement-detail'),
    #path('sections/<uuid:pk>/requirements/<uuid:requirement_id>/statements/<uuid:statement_id>/constraints/<uuid:constraint_id>/', views.ConstraintDetail.as_view(), name='task-detail'),
    path('sections/<uuid:pk>/requirements/create/', views.RequirementCreate.as_view(), name='requirement-create'),
    path('requirements/<uuid:pk>/delete', views.RequirementDelete.as_view(), name='requirement-delete'),
    path('requirements/<uuid:pk>/update', views.RequirementUpdate.as_view(), name='requirement-update'),
    path('requirements/<uuid:pk>/statements/create/', views.StatementCreate.as_view(), name='statement-create'),
    path('statements/<uuid:pk>/delete', views.StatementDelete.as_view(), name='statement-delete'),
    path('statements/<uuid:pk>/update', views.StatementUpdate.as_view(), name='statement-update'),
    path('statements/<uuid:pk>/constraints/create/', views.ConstraintCreate.as_view(), name='constraint-create'),
    path('constraints/<uuid:pk>/delete', views.ConstraintDelete.as_view(), name='constraint-delete'),
    path('constraints/<uuid:pk>/update', views.ConstraintUpdate.as_view(), name='constraint-update'),
]
