import logging

from django_components import component
from django.shortcuts import get_object_or_404

from projects.models import Sprint, Backlog
from workflows.tenant import current_tenant_id
from workflows.tenant_models import tenant_check

@component.register("board_list")
class BoardList(component.Component):
    template_name = "board/board_list.html"

    def get_context_data(self, *args, **kwargs):
        if "board" not in kwargs:
            raise ValueError("board required")
        if "list" not in kwargs:
            raise ValueError("list required")

        tenant_id = kwargs.get("tenant_id", None) or current_tenant_id()

        return {
            "board": kwargs.get("board"),
            "list": kwargs["list"],
            "tenant_id": tenant_id,
        }

    def get_list(self, tenant_id, request):
        list_id = request.POST.get('list_id')
        if not list_id:
            raise ValueError(f"list_id is required")
        try:
            return Sprint.unscoped.get(tenant_id=tenant_id, id=list_id)
        except Sprint.DoesNotExist:
            raise ValueError(f"Sprint {list_id} does not exist")

    def get_board(self, tenant_id, request):
        board_id = request.POST.get('board_id')
        if not board_id:
            raise ValueError(f"board_id is required")
        try:
            return Backlog.unscoped.get(tenant_id=tenant_id, id=board_id)
        except Backlog.DoesNotExist:
            raise ValueError(f"Backlog {board_id} does not exist")

    def get_context(self, tenant_id, request):
        list = self.get_list(tenant_id, request)
        board = self.get_board(tenant_id, request)

        return {
            "board": board,
            "list": list,
            "tenant_id": tenant_id,
        }

    def start_sprint(self, tenant_id, request):
        context = self.get_context(tenant_id, request)
        project = context["board"].project
        sprint = context["list"]
        project.start_sprint(sprint)
        return context

    def end_sprint(self, tenant_id, request):
        context = self.get_context(tenant_id, request)
        project = context["board"].project
        sprint = context["list"]
        project.end_sprint(sprint)
        return context

    def post(self, request, *args, **kwargs):
        tenant_id = kwargs['tenant_id']
        op = kwargs['op']

        if op == "start-sprint":
            context = self.start_sprint(tenant_id, request)
        elif op == "end-sprint":
            context = self.end_sprint(tenant_id, request)
        else:
            raise ValueError(f"Invalid op: {op}")

        return self.render_to_response(kwargs=context)
