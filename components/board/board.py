import logging

from django_components import component

from workflows.tenant import current_tenant_id

@component.register("board")
class Board(component.Component):
    template_name = "board/board.html"

    def get_context_data(self, **kwargs):

        if "board" not in kwargs:
            raise ValueError("board required")

        tenant_id = current_tenant_id()

        breakpoint()
        return {
            "board": kwargs["board"],
            "tenant_id": kwargs["tenant_id"],
        }

    class Media:
        #css = "board/board.css"
        js = "board/board.js"
