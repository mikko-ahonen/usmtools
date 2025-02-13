from django.utils.translation import gettext_lazy as _


class EntityType:
    NOT_DEFINED = "not-defined"
    DOCUMENT = "document"
    TASK = "task"
    ROUTINE = "routine"
    PROFILE = "profile"

    CHOICES = [
        (NOT_DEFINED, _("Not defined")),
        (DOCUMENT, _("Document")),
        (TASK, _("Task")),
        (ROUTINE, _("Routine")),
        (PROFILE, _("Profile")),
    ]

def get_class_by_entity_type(entity_type):
    match entity_type:

        case EntityType.DOCUMENT:
            from mir.models import Document
            return Document

        case EntityType.TASK:
            from compliances.models import Task
            return Task

        case EntityType.ROUTINE:
            from compliances.models import Routine
            return Routine

        case EntityType.PROFILE:
            from compliances.models import Profile
            return Profile

        case _:
            raise ValueError(f"Unsupported entity type: {entity_type}")
