from django.db import models

import uuid
from boards.models import Board, List, Task

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from workflows.tenant_models import TenantAwareOrderedModelBase, TenantAwareTreeModelBase, TenantAwareModelBase

class Project(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    prefix = models.CharField(max_length=255, blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'

    def __str__(self):
        return self.name or ""

    class Meta:
        ordering = ('index',)

class Release(List):
    _show_list_count = False
    list_type = List.LIST_TYPE_RELEASE
    board = models.ForeignKey('Roadmap', on_delete=models.CASCADE, related_name="lists")

    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def epics(self):
        return self.tasks

    class Meta(List.Meta):
        verbose_name = "release"
        verbose_name_plural = "releases"

class Sprint(List, Board):
    _max_columns = 4
    _show_list_count = False
    board_type = Board.BOARD_TYPE_SPRINT
    list_type = List.LIST_TYPE_SPRINT
    board = models.ForeignKey('Backlog', on_delete=models.CASCADE, related_name="lists")

    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def stories(self):
        return self.tasks

    class Meta(List.Meta):
        verbose_name = "sprint"
        verbose_name_plural = "sprints"

class Epic(Task):
    _default_task_type = Task.TASK_TYPE_EPIC
    list = models.ForeignKey(Release, on_delete=models.CASCADE, related_name="tasks")

    class Meta(Task.Meta):
        verbose_name = "epic"
        verbose_name_plural = "epics"

class Story(Task):
    list = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name="tasks")

    task_type = Task.TASK_TYPE_STORY

    class Meta(Task.Meta):
        verbose_name = "story"
        verbose_name_plural = "stories"

class Roadmap(Board):
    _max_columns = 1
    board_type = Board.BOARD_TYPE_ROADMAP
    list_class = Release
    task_class = Epic

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        null=True,
        related_name='roadmap',
    )

    @property
    def releases(self):
        return self.lists

    class Meta(Board.Meta):
        verbose_name = "roadmap"
        verbose_name_plural = "roadmaps"

class Backlog(Board):
    _max_columns = 1
    board_type = Board.BOARD_TYPE_BACKLOG
    list_class = Sprint
    task_class = Story

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        null=True,
        related_name='backlog',
    )

    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def sprints(self):
        return self.lists

    class Meta(Board.Meta):
        verbose_name = "backlog"
        verbose_name_plural = "backlogs"
