from django.urls import path

from django.views.generic.base import RedirectView

#from components.status_board.status_board import StatusBoard
from components.board.board_list import BoardList

app_name = "components"

urlpatterns = [
    #path('<uuid:tenant_id>/components/status-board/items/<slug:slug>', StatusBoard.as_view(), name='status-board-items'),
    path('<uuid:tenant_id>/components/board/board-list/<str:op>/', BoardList.as_view(), name='board-list'),
]
