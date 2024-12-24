from django.urls import path
from boards import views
from django.views.generic.base import RedirectView

app_name = "boards"

urlpatterns = [
    # boards:
    path('', RedirectView.as_view(url='/workflows/tenants/')),
    path("<uuid:tenant_id>/", views.boards, name="boards"),
    path("<uuid:tenant_id>/<str:board_type>/create_board/", views.create_board, name="create_board"),
    path("<uuid:tenant_id>/<str:board_type>/<uuid:board_uuid>/", views.board, name="board"),
    # lists:

    path("<uuid:tenant_id>/<str:board_type>/<uuid:board_uuid>/create_list/", views.create_list, name="create_list"),
    path(
        "<uuid:tenant_id>/<str:board_type>/<uuid:board_uuid>/<uuid:list_uuid>/delete_list/",
        views.delete_list,
        name="delete_list",
    ),
    # tasks:
    path(
        "<uuid:tenant_id>/<str:board_type>/<uuid:board_uuid>/<uuid:list_uuid>/create_task/",
        views.create_task,
        name="create_task",
    ),
    path(
        "<uuid:tenant_id>/<str:board_type>/<uuid:board_uuid>/<uuid:task_uuid>/edit_task/",
        views.edit_task,
        name="edit_task",
    ),
    path(
        "<uuid:tenant_id>/<str:board_type>/<uuid:task_uuid>/task_modal/",
        views.task_modal,
        name="task_modal",
    ),
    path("<uuid:tenant_id>/<str:board_type>/<uuid:board_uuid>/list_move/", views.list_move, name="list_move"),
    path("<uuid:tenant_id>/<str:board_type>/<uuid:board_uuid>/task_move/", views.task_move, name="task_move"),
]
