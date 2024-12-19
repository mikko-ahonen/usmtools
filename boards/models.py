import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

class Board(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    uuid = models.UUIDField(verbose_name=_("UUID"), default=uuid.uuid4, editable=False, unique=True)
    text = models.TextField(verbose_name=_("Text"), null=True, blank=True)

    def get_absolute_url(self):
        return reverse("boards:board", kwargs={"board_uuid": self.uuid})

    def create_default_lists(self):
        for name in ["Todo", "Doing", "Done"]:
            List.objects.create(name=name, board=self)

    def __str__(self) -> str:
        return self.name


class List(models.Model):
    name = models.CharField("Name", max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="lists")
    order = models.SmallIntegerField(default=1000, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    LIST_TYPE_RELEASE = "release"
    LIST_TYPE_SPRINT = "sprint"
    LIST_TYPE_STATUS = "status"
    LIST_TYPES = [
        (LIST_TYPE_RELEASE, _("Release")),
        (LIST_TYPE_SPRINT, _("Sprint")),
        (LIST_TYPE_STATUS, _("Status")),
    ]
    type = models.CharField(max_length=32, choices=LIST_TYPES, default=LIST_TYPE_RELEASE)

    def __str__(self) -> str:
        return f"{self.name} ({self.order})"

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

class Task(models.Model):
    label = models.TextField("Label")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="tasks")
    order = models.SmallIntegerField(default=1000, db_index=True)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    TASK_TYPE_EPIC = "epic"
    TASK_TYPE_STORY = "story"
    TASK_TYPES = [
        (TASK_TYPE_EPIC, _("Epic")),
        (TASK_TYPE_STORY, _("Story")),
    ]
    type = models.CharField(max_length=32, choices=TASK_TYPES, default=TASK_TYPE_EPIC)

    def __str__(self) -> str:
        return self.label

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
