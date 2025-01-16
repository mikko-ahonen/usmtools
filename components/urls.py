from django.urls import path

from django.views.generic.base import RedirectView

from components.board.board import Board
from components.board.board_list import BoardList

app_name = "components"

urlpatterns = [
    #path('<uuid:tenant_id>/components/status-board/items/<slug:slug>', StatusBoard.as_view(), name='status-board-items'),
    path('<uuid:tenant_id>/components/board/board-list/<str:op>/', BoardList.as_view(), name='board-list'),
    path('<uuid:tenant_id>/components/board/<str:board_type>/<uuid:board_id>/<str:op>/', Board.as_view(), name='board'),
    path('<uuid:tenant_id>/components/board/<str:board_type>/<uuid:board_id>/<str:op>/<uuid:team_id>/', Board.as_view(), name='board-team'),
]
