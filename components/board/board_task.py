import logging

from django_components import component
from workflows.tenant import current_tenant_id

@component.register("board_task")
class BoardTask(component.Component):
    template_name = "board/board_task.html"

    def get_context_data(self, *args, **kwargs):
        if "board" not in kwargs:
            raise ValueError("board required")
        if "list" not in kwargs:
            raise ValueError("list required")
        if "task" not in kwargs:
            raise ValueError("task required")

        tenant_id = current_tenant_id()

        return {
            "tenant_id": tenant_id,
            "board": kwargs.get("board"),
            "list": kwargs["list"],
            "task": kwargs["task"],
        }
