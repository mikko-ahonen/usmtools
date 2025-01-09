import logging

from django_components import component

from workflows.tenant import current_tenant_id

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

    class Media:
        #css = "board/board.css"
        js = "board/board.js"
