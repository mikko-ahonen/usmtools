from django import template

register = template.Library()

@register.filter
def board_css_class(board, is_last):
    if board._max_columns == 1:
        return "col-md-12"
    elif board._max_columns == 2:
        return "col-md-6"
    elif board._max_columns == 3:
        return "col-md-4"
    elif board._max_columns == 4:
        return "col-md-3"
    elif board._max_columns == 5:
        if is_last:
            return "col-md-auto"
        return "col-md-2"
    elif board._max_columns == 6:
        return "col-md-2"
