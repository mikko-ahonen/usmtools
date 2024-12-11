import logging

from django_components import component
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

@component.register("status_board_column")
class StatusBoardColumn(component.Component):
    template_name = "status_board/status_board_column.html"

    def get_context_data(self, **kwargs):
        if "column_slug" not in kwargs:
            raise ValueError("column_slug required")
        if "root_id" not in kwargs:
            raise ValueError("root_id required")
        if "entities" not in kwargs:
            raise ValueError("entities required")
        if "column" not in kwargs:
            raise ValueError("column required")

        return {
            "root_id": kwargs.get("root_id", None),
            "column_slug": kwargs.get("column_slug", None),
            "column": kwargs.get("column", []),
            "entities": kwargs.get("entities", []),
        }
