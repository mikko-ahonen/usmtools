import logging

from django_components import component

@component.register("board_list")
class BoardList(component.Component):
    template_name = "board/board_list.html"

    def get_context_data(self, **kwargs):
        if "tenant_id" not in kwargs:
            raise ValueError("tenant_id required")
        if "board" not in kwargs:
            raise ValueError("board required")
        if "list" not in kwargs:
            raise ValueError("list required")
        breakpoint()
        return {
            "tenant_id": kwargs.get("tenant_id"),
            "board": kwargs.get("board"),
            "list": kwargs["list"],
        }
