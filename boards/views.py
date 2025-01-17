import uuid
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django import forms
from django.db import models
from django.views.decorators.http import require_POST
from django.db.models import Case, When, F
from django.apps import apps

from workflows.tenant import current_tenant_id
from boards.models import Board, List, Task

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

def boards(request, tenant_id):
    boards = Board.objects.all()
    tenant_id = current_tenant_id()
    return render(request, "boards/boards.html", {"tenant_id": tenant_id, "boards": boards})

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ["name", "text"]

def create_board(request, tenant_id, board_type):
    board_cls = get_board_class_by_type(board_type)
    form_cls = BoardForm
    form_cls.Meta.model = board_cls
    form = form_cls(request.POST or None)

    if request.method == "POST" and form.is_valid():
        board = form.save()
        board.create_default_lists()
        return HttpResponse(
            status=204, headers={"HX-Redirect": board.get_absolute_url()}
        )

    tenant_id = current_tenant_id()

    return render(request, "boards/board_form.html", {"tenant_id": tenant_id, "form": form})


def board(request, tenant_id, board_type, board_uuid, partial=False):
    board_cls = get_board_class_by_type(board_type)
    board = get_object_or_404(
        board_cls.unscoped.filter(tenant_id=tenant_id), id=board_uuid
    )
    template = "boards/_board.html" if partial else "boards/board.html"
    tenant_id = current_tenant_id()

    response = render(request, template, {"tenant_id": tenant_id, "board": board})
    response["HX-Retarget"] = "#board"
    return response


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name"]


#def list_form_factory(model):
#    name = model.__name__ + 'Form'
#    parents = (forms.ModelForm,)
#    attrs = {
#        'Meta': type('Meta', (object,), {'model': model, 'fields': ['name']}),
#    }
#    return ModelFormMetaclass(name, parents, attrs)

def create_list(request, tenant_id, board_type, board_uuid):
    board_cls = get_board_class_by_type(board_type)
    list_cls = get_list_class_by_type(board_type)
    board = get_object_or_404(board_cls, id=board_uuid)
    form_cls = ListForm
    form_cls.Meta.model = list_cls
    form = form_cls(request.POST or None)

    tenant_id = current_tenant_id()

    if request.method == "POST" and form.is_valid():
        form.instance.board = board
        form.save()
        return board(request, tenant_id, board_type, board_uuid, partial=True)

    return render(request, "boards/board_form.html", {"tenant_id": tenant_id, "form": form})


def delete_list(request, tenant_id, board_type, board_uuid, list_uuid):
    list_cls = get_list_class_by_type(board_type)
    list = get_object_or_404(list_cls, id=list_uuid)

    if request.method == "POST":
        list.delete()

    tenant_id = current_tenant_id()

    return board(request, tenant_id, board_type, board_uuid, partial=True)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description"]


def create_task(request, tenant_id, board_type, board_uuid, list_uuid):
    list_cls = get_list_class_by_type(board_type)
    task_cls = get_task_class_by_type(board_type)
    list = get_object_or_404(list_cls, id=list_uuid)
    form_cls = TaskForm
    form_cls.Meta.model = task_cls
    form = form_cls(request.POST or None)

    tenant_id = current_tenant_id()

    if request.method == "POST" and form.is_valid():
        form.instance.list = list
        task = form.save()
        return board(request, tenant_id, board_type, board_uuid, partial=True)

    return render(request, "boards/board_form.html", {"tenant_id": tenant_id, "form": form})


def edit_task(request, tenant_id, board_type, board_uuid, task_uuid):
    task_cls = get_task_class_by_type(board_type)
    task = get_object_or_404(task_cls, id=task_uuid)
    form_cls = TaskForm
    form_cls.Meta.model = task_cls
    form = form_cls(request.POST or None, instance=task)

    tenant_id = current_tenant_id()
    if request.method == "POST" and form.is_valid():
        task = form.save()
        return board(request, tenant_id, board_type, board_uuid, partial=True)

    return render(request, "boards/board_form.html", {"tenant_id": tenant_id, "form": form})


class TypedMultipleField(forms.TypedMultipleChoiceField):
    def __init__(self, *args, coerce, **kwargs):
        super().__init__(*args, **kwargs)
        self.coerce = self.coerce

    def valid_value(self, value):
        # all choices are okay
        return True


class ListMoveForm(forms.Form):
    list_uuids = TypedMultipleField(coerce=uuid.UUID)


def preserve_order(uuids):
    return Case(
        *[When(id=uuid, then=o) for o, uuid in enumerate(uuids)],
        default=F("index"),
        output_field=models.IntegerField()
    )


@require_POST
def list_move(request, tenant_id, board_type, board_uuid):
    form = ListMoveForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(str(form.errors))

    list_uuids = form.cleaned_data["list_uuids"]
    list_cls = get_list_class_by_type(board_type)
    list_cls.objects.filter(uuid__in=list_uuids).update(index=preserve_order(list_uuids))
    tenant_id = current_tenant_id()
    return board(request, tenant_id, board_type, board_uuid, partial=True)


class TaskMoveForm(forms.Form):
    item = forms.UUIDField()
    from_list = forms.UUIDField()
    to_list = forms.UUIDField()
    task_uuids = TypedMultipleField(coerce=uuid.UUID)


@require_POST
def task_move(request, tenant_id, board_type, board_uuid):
    form = TaskMoveForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(str(form.errors))

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

    tenant_id = current_tenant_id()
    return board(request, tenant_id, board_type, board_uuid, partial=True)


def task_modal(request, tenant_id, board_type, task_uuid):
    task_cls = get_task_class_by_type(board_type)
    task = get_object_or_404(task_cls.objects.select_related("list"), id=task_uuid)
    form_cls = TaskForm
    form_cls.Meta.model = task_cls
    form = form_cls(request.POST or None, instance=task)

    if request.method == "POST" and form.is_valid():
        task = form.save()
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})

    tenant_id = current_tenant_id()
    return render(request, "boards/task_modal.html", {"tenant_id": tenant_id, "task": task, "form": form})
