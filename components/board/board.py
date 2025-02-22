import uuid
import logging

from django_components import component
from django import forms
from django.db.models import Case, When, F
from django.apps import apps
from django.shortcuts import get_object_or_404
from django.db import models

from projects.models import Team, Sprint

from workflows.tenant import current_tenant_id

   
def preserve_order(uuids):
    return Case(
        *[When(id=uuid, then=o) for o, uuid in enumerate(uuids)],
        default=F("index"),
        output_field=models.IntegerField()
    )

def get_board_class_by_type(board_type):
    if board_type == 'roadmap':
        return apps.get_model('projects', 'Roadmap')
    elif board_type == 'backlog':
        return apps.get_model('projects', 'Backlog')
    elif board_type == 'sprint':
        return apps.get_model('projects', 'Sprint')
    else:
        raise ValueError(f"Invalid board type: {board_type}")

def get_list_class_by_type(board_type):
    board_cls = get_board_class_by_type(board_type)
    if isinstance(board_cls.list_class, tuple):
        return apps.get_model(*board_cls.list_class)
    return board_cls.list_class

def get_task_class_by_type(board_type):
    board_cls = get_board_class_by_type(board_type)
    if isinstance(board_cls.task_class, tuple):
        return apps.get_model(*board_cls.task_class)
    return board_cls.task_class

class TypedMultipleField(forms.TypedMultipleChoiceField):
    def __init__(self, *args, coerce, **kwargs):
        super().__init__(*args, **kwargs)
        self.coerce = self.coerce
        
    def valid_value(self, value):
        # all choices are okay
        return True

class TaskMoveForm(forms.Form):
    item = forms.UUIDField()
    from_list = forms.UUIDField()
    to_list = forms.UUIDField()
    task_uuids = TypedMultipleField(coerce=uuid.UUID)

class ListMoveForm(forms.Form):
    list_uuids = TypedMultipleField(coerce=uuid.UUID)
    
@component.register("board")
class Board(component.Component):
    template_name = "board/board.html"

    def get_context_data(self, **kwargs):

        if "board" not in kwargs:
            raise ValueError("board required")

        if "lists" not in kwargs:
            raise ValueError("lists required")

        tenant_id = current_tenant_id()

        return {
            "board": kwargs["board"],
            "lists": kwargs["lists"],
            "tenant_id": tenant_id,
        }

    def list_move(self, request, tenant_id, board_type, board_id):
        form = ListMoveForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest(str(form.errors))

        list_uuids = form.cleaned_data["list_uuids"]
        list_cls = get_list_class_by_type(board_type)
        list_cls.objects.filter(id__in=list_uuids).update(index=preserve_order(list_uuids))

        return self.get_context(board_type, board_id)

    def task_move(self, request, tenant_id, board_type, board_id, team_id=None):

        form = TaskMoveForm(request.POST)

        if not form.is_valid():
            return HttpResponseBadRequest(str(form.errors))

        board_cls = get_board_class_by_type(board_type)
        board = get_object_or_404(
            board_cls.unscoped.filter(tenant_id=tenant_id), id=board_id
        )

        from_list = form.cleaned_data["from_list"]
        to_list = form.cleaned_data["to_list"]
        task_uuids = form.cleaned_data["task_uuids"]
        item_uuid = form.cleaned_data["item"] 
    
        list_cls = get_list_class_by_type(board_type)
        task_cls = get_task_class_by_type(board_type)
        if to_list == from_list:
            task_cls.objects.filter(id__in=task_uuids).update(
                index=preserve_order(task_uuids)
            )
        else:
            task_cls.objects.filter(id__in=task_uuids).update(
                index=preserve_order(task_uuids),
                list_id=list_cls.objects.filter(id=to_list).order_by().values("id"),
            )

        return self.get_context(board_type, board_id, team_id)


    def get_board(self, tenant_id, board_type, board_id):
        board_cls = get_board_class_by_type(board_type)
        board = get_object_or_404(board_cls, id=board_id)
        return board

    def get_context(self, board_type, board_id, team_id=None):

        tenant_id = current_tenant_id()

        if board_type == 'backlog':
            lists = Sprint.unscoped.filter(tenant_id=tenant_id, board_id=board_id, status__in=[Sprint.STATUS_NEW, Sprint.STATUS_READY, Sprint.STATUS_ONGOING]).order_by('index')

        elif board_type == 'sprint':
            assert team_id, "team_id required"
            team = get_object_or_404(Team, id=team_id)
            lists = team.current_sprint.lists.order_by('index')

        elif board_type == 'roadmap':
            lists = Release.unscoped.filter(tenant_id=tenant_id, board_id=board_id, status__in=[Release.STATUS_NEW, Release.STATUS_READY, Release.STATUS_ONGOING]).order_by('index')

        else:
            raise ValueError(f"Invalid board type: {board_type}")

        board = self.get_board(tenant_id, board_type, board_id)

        return {
            "tenant_id": tenant_id,
            "lists": lists,
            "board": board,
        }



    def post(self, request, *args, **kwargs):
        tenant_id = kwargs['tenant_id']
        board_type = kwargs['board_type']
        board_id = kwargs['board_id']

        op = kwargs['op']

        if op == "task-move":
            team_id = kwargs.get('team_id', None)
            if board_type == 'sprint':
                assert team_id, "team_id is required"
            context = self.task_move(request, tenant_id, board_type, board_id, team_id=team_id)
        elif op == "list-move":
            context = self.list_move(request, tenant_id, board_type, board_id)
        else:
            raise ValueError(f"Invalid op: {op}")

        return self.render_to_response(kwargs=context)

    class Media:
        pass
        #css = "board/board.css"
        #js = "board/board.js"



