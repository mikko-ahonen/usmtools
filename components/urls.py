from django.urls import path

from django.views.generic.base import RedirectView

from components.status_board.status_board import StatusBoard

app_name = "components"

urlpatterns = [
    path('<uuid:tenant_id>/components/status-board/items/<slug:slug>', StatusBoard.as_view(), name='status-board-items'),
]
