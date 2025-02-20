from django.urls import path

from django.views.generic.base import RedirectView

from components.tags.action_tags import ActionTags
from components.tags.routine_tags import RoutineTags
from components.tags.document_tags import DocumentTags
from components.board.board import Board
from components.board.board_list import BoardList
from components.typeahead.typeahead import Typeahead
from components.typeahead.typeahead_results import TypeaheadResults
from components.entity_selector.responsibility_profile_selector import ResponsibilityProfileSelector
from components.entity_selector.definition_reference_selector import DefinitionReferenceSelector
from components.constraint_references.constraint_references import ConstraintReferences
from components.constraint.constraint_editor import ConstraintEditor
from components.action.responsibility_editor import ResponsibilityEditor
from components.action.action_editor import ActionEditor

app_name = "components"

urlpatterns = [
    #path('<uuid:tenant_id>/components/status-board/items/<slug:slug>', StatusBoard.as_view(), name='status-board-items'),
    path('<uuid:tenant_id>/components/board/board-list/<str:op>/', BoardList.as_view(), name='board-list'),
    path('<uuid:tenant_id>/components/board/<str:board_type>/<uuid:board_id>/<str:op>/', Board.as_view(), name='board'),
    path('<uuid:tenant_id>/components/board/<str:board_type>/<uuid:board_id>/<str:op>/<uuid:team_id>/', Board.as_view(), name='board-team'),
    path('<uuid:tenant_id>/components/tags/routine-tags/', RoutineTags.as_view(), name='routine-tags'),
    path('<uuid:tenant_id>/components/tags/action-tags/', ActionTags.as_view(), name='action-tags'),
    path('<uuid:tenant_id>/components/tags/document-tags/', DocumentTags.as_view(), name='document-tags'),
    path("<uuid:tenant_id>/typeahead/select/", Typeahead.as_view(), name='typeahead-select'),
    path("<uuid:tenant_id>/typeahead/search/", TypeaheadResults.as_view(), name='typeahead-search'),
    path("<uuid:tenant_id>/components/responsibilities/profiles/select", ResponsibilityProfileSelector.as_view(), name='responsibility-select-profile'),
    path("<uuid:tenant_id>/components/definitions/references/select/<str:entity_type>/", DefinitionReferenceSelector.as_view(), name='definition-select-reference'),
    path("<uuid:tenant_id>/<uuid:domain_id>/constraints/references/", ConstraintReferences.as_view(), name='constraint-references'),
    path("<uuid:tenant_id>/<uuid:domain_id>/constraints/<uuid:constraint_id>/editor/", ConstraintEditor.as_view(), name='constraint-editor'),
    path("<uuid:tenant_id>/responsibilities/<uuid:responsibility_id>/editor/", ResponsibilityEditor.as_view(), name='responsibility-editor'),
    path("<uuid:tenant_id>/actions/<uuid:action_id>/responsibilities/create/", ActionEditor.as_view(), name='responsibility-create'),
    path("<uuid:tenant_id>/responsibilities/<uuid:responsibility_id>/delete/", ActionEditor.as_view(), name='responsibility-delete'),
]
