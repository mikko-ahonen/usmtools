import logging

from django_components import component

logger = logging.getLogger(__name__)

@component.register("status-board")
class StatusBoard(component.Component):
    template_name = "status_board/status_board.html"

    def get_context_data(self, **kwargs):
        if "entities" not in kwargs:
            raise ValueError("entities required")
        if "columns" not in kwargs:
            raise ValueError("columns required")
        return {
            "columns": kwargs.get("columns", []),
            "entities": kwargs.get("entities", []),
        }

    class Media:
        css = "status_board/status_board.css"

