import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from workflows.tenant import current_tenant_id
from workflows.tenant_models import TenantAwareOrderedModelBase, TenantAwareTreeModelBase, TenantAwareModelBase

class Board(TenantAwareModelBase):
    _max_columns = 4

    name = models.CharField(verbose_name=_("Name"), max_length=255)
    uuid = models.UUIDField(verbose_name=_("UUID"), default=uuid.uuid4, editable=False, unique=True)
    text = models.TextField(verbose_name=_("Text"), null=True, blank=True)

    BOARD_TYPE_GENERIC = "generic"
    BOARD_TYPE_ROADMAP = "roadmap"
    BOARD_TYPE_BACKLOG = "backlog"
    BOARD_TYPE_SPRINT = "sprint"
    BOARD_TYPES = [
        (BOARD_TYPE_GENERIC, _("Board")),
        (BOARD_TYPE_ROADMAP, _("Roadmap")),
        (BOARD_TYPE_BACKLOG, _("Backlog")),
        (BOARD_TYPE_SPRINT, _("Sprint")),
    ]

    def get_absolute_url(self):
        tenant_id = current_tenant_id()
        return reverse("boards:board", kwargs={"tenant_id": tenant_id, "board_uuid": self.uuid})

    def create_default_lists(self):
        for name in ["Todo", "Doing", "Done"]:
            List.objects.create(name=name, board=self)

    class Meta:
        verbose_name = "board"
        verbose_name_plural = "boards"

    def __str__(self) -> str:
        return self.name

class List(TenantAwareOrderedModelBase):
    _show_list_count = False

    name = models.CharField("Name", max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="lists")
    index = models.SmallIntegerField(default=1000, db_index=True)

    LIST_TYPE_RELEASE = "release"
    LIST_TYPE_SPRINT = "sprint"
    LIST_TYPE_STATUS = "status"
    LIST_TYPES = [
        (LIST_TYPE_RELEASE, _("Release")),
        (LIST_TYPE_SPRINT, _("Sprint")),
        (LIST_TYPE_STATUS, _("Status")),
    ]

    order_field_name = 'index'

    def __str__(self) -> str:
        return f"{self.name} ({self.index})"

    class Meta:
        verbose_name = "list"
        verbose_name_plural = "lists"
        
        ordering = ["index"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

class Task(TenantAwareOrderedModelBase):
    label = models.TextField("Label")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="tasks")
    index = models.SmallIntegerField(default=1000, db_index=True)
    description = models.TextField(verbose_name=_("Description"), blank=True)

    TASK_TYPE_EPIC = "epic"
    TASK_TYPE_STORY = "story"
    TASK_TYPES = [
        (TASK_TYPE_EPIC, _("Epic")),
        (TASK_TYPE_STORY, _("Story")),
    ]

    order_field_name = 'index'

    def __str__(self) -> str:
        return self.label

    class Meta:
        verbose_name = "task"
        verbose_name_plural = "tasks"
        ordering = ["index"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
