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

    @classmethod
    def get_by_name(cls, s):
        s = s.strip().lower()
        for entity_type, name in cls.CHOICES:
            if entity_type == s:
                return entity_type
        return None
        

def get_class_by_entity_type(entity_type):
    match entity_type:

        case EntityType.NOT_DEFINED:
            return None

        case EntityType.DOCUMENT:
            from mir.models import Document
            return Document

        case EntityType.TASK:
            from workflows.models import Task
            return Task

        case EntityType.ROUTINE:
            from workflows.models import Routine
            return Routine

        case EntityType.PROFILE:
            from workflows.models import Profile
            return Profile

        case _:
            raise ValueError(f"Unsupported entity type: {entity_type}")
