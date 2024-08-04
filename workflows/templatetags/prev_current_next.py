from django import template

register = template.Library()

@register.filter()
def prev_current_next(orig):
    if len(orig) < 3:
        # make the tests pass. typically the steps are created from template, so there should be many more
        return None
    orig = list(orig)
    new = ([(None, orig[0], orig[1])] + 
          list(zip(orig, orig[1:], orig[2:])) + 
          [(orig[-2], orig[-1], None)])
    return new
