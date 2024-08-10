import logging

from django_components import component

logger = logging.getLogger(__name__)

@component.register("status_board_column")
class StatusBoardColumn(component.Component):
    template_name = "status_board/status_board_column.html"

    def get_context_data(self, **kwargs):
        if "entities" not in kwargs:
            raise ValueError("entities required")
        if "column" not in kwargs:
            raise ValueError("column required")
        return {
            "column": kwargs.get("columns", []),
            "entities": kwargs.get("entities", []),
        }
