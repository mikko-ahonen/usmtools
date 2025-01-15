from django.db import models

import uuid
from boards.models import Board, List, Task

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from sequences import get_next_value

from workflows.tenant_models import TenantAwareOrderedModelBase, TenantAwareTreeModelBase, TenantAwareModelBase

def get_next_task_number():
    return get_next_value('task')

class Project(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    prefix = models.CharField(max_length=255, blank=True, null=True, default="ISO27K")
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    start_date = models.DateField(null=True, blank=True, default="2025-01-01")
    sprint_length_in_days = models.PositiveSmallIntegerField(default=21)
    release_length_in_days = models.PositiveSmallIntegerField(default=21)
    epics_per_release = models.PositiveSmallIntegerField(default=2)
    story_points_in_sprint = models.PositiveSmallIntegerField(default=10)
    ideal_story_points_per_day = models.PositiveSmallIntegerField(default=10, help_text=_('Accross all teams. Used to estimate the project cmpletion date, for example in the burndown chart.'))

    order_field_name = 'index'

    def __str__(self):
        return self.name or ""

    def get_current_release(self):
        return self.roadmap.releases.filter(status=Release.STATUS_ONGOING).first()

    def get_active_sprints(self):
        return Sprint.unscoped.filter(tenant_id=self.tenant_id, project_id=self.id, status=Sprint.STATUS_ONGOING)

    def start_sprint(self, sprint):

        team = sprint.team

        if team.current_sprint:
            raise ValueError(f"There is already a current sprint {team.current_sprint} for team {team}. You must stop it first.")

        team.current_sprint = sprint
        team.save()
        sprint.status = Sprint.STATUS_ONGOING
        sprint.save()

    def get_epics(self):
        qs = None
        for release in self.roadmap.releases.all():
            if qs:
                qs = qs.union(release.epics.all())
            else:
                qs = release.epics.all()
        return qs

    def stop_sprint(self, sprint):

        team = sprint.team
        if not team.current_sprint:
            raise ValueError(f"Team {team} has no current sprint.")
        self.current_sprint.status = Sprint.STATUS_CLOSED
        self.current_sprint.save()
        self.current_sprint = None
        self.save()

    class Meta:
        ordering = ('index',)

class Team(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, related_name='teams')
    current_sprint = models.ForeignKey('Sprint', on_delete=models.PROTECT, null=True, blank=True, related_name="+")

    order_field_name = 'index'

    def __str__(self):
        return self.name or str(self.id)

    class Meta:
        ordering = ('index',)

class Release(List):
    _show_list_count = False
    list_type = List.LIST_TYPE_RELEASE
    board = models.ForeignKey('Roadmap', on_delete=models.CASCADE, related_name="lists")

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    STATUS_NEW = "new"
    STATUS_READY = "ready"
    STATUS_ONGOING = "ongoing"
    STATUS_CLOSED = "closed"
    STATUSES = [
        (STATUS_NEW, _("New")),
        (STATUS_READY, _("Ready")),
        (STATUS_ONGOING, _("Ongoing")),
        (STATUS_CLOSED, _("Closed")),
    ]
    status = models.CharField(max_length=32, choices=STATUSES, default=STATUS_NEW)

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
    list_class = ('projects', 'Status')
    task_class = ('projects', 'Story')
    board = models.ForeignKey('Backlog', on_delete=models.CASCADE, related_name="lists")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.PROTECT)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="sprints", null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    STATUS_NEW = "new"
    STATUS_READY = "ready"
    STATUS_ONGOING = "ongoing"
    STATUS_CLOSED = "closed"
    STATUSES = [
        (STATUS_NEW, _("New")),
        (STATUS_READY, _("Ready")),
        (STATUS_ONGOING, _("Ongoing")),
        (STATUS_CLOSED, _("Closed")),
    ]
    status = models.CharField(max_length=32, choices=STATUSES, default=STATUS_NEW)

    def is_first_inactive_sprint_for_team(self):
        first_inactive_sprint = self.board.lists.filter(team=self.team, status__in=[self.STATUS_NEW, self.STATUS_READY]).order_by('index').first()
        if first_inactive_sprint:
            return self.id == first_inactive_sprint.id
        return False

    def create_default_lists(self):
        for i, (slug, name) in enumerate(self.STATUSES, start=1):
            c = Status(tenant_id=self.tenant_id, slug=slug, name=name, board=self, index=i)
            c.save()

    @property
    def tasks(self):
        return self.stories

    @property
    def stories(self):
        list_ids = [l.id for l in self.lists.all()]
        return Story.unscoped.filter(tenant_id=self.tenant_id, list_id__in=list_ids)

    class Meta(List.Meta):
        verbose_name = "sprint"
        verbose_name_plural = "sprints"


class Status(List):
    _max_columns = 4
    list_type = List.LIST_TYPE_STATUS
    board = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name="lists")
    slug = models.CharField(max_length=32, choices=Sprint.STATUSES, default=Sprint.STATUS_NEW)


class Epic(Task):
    list = models.ForeignKey(Release, on_delete=models.CASCADE, related_name="tasks")
    task_type = Task.TASK_TYPE_EPIC
    _story_points = None

    category = models.ForeignKey('compliances.Category', null=True, blank=True, on_delete=models.PROTECT)
    number = models.PositiveSmallIntegerField(editable=False, db_index=True, default=get_next_task_number)

    def get_story_points(self):
        if not self._story_points:
            story_points = 0
            for story in self.story_set.all():
                story_points += story.story_points
            self._story_points = story_points
        return self._story_points

    class Meta(Task.Meta):
        verbose_name = "epic"
        verbose_name_plural = "epics"

class Story(Task):
    list = models.ForeignKey(Status, on_delete=models.CASCADE, related_name="tasks")

    task_type = Task.TASK_TYPE_STORY

    number = models.PositiveSmallIntegerField(editable=False, db_index=True, default=get_next_task_number)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.PROTECT)
    epic = models.ForeignKey(Epic, null=True, blank=True, on_delete=models.SET_NULL)
    constraint = models.ForeignKey('compliances.Constraint', null=True, blank=True, on_delete=models.PROTECT)
    story_points = models.FloatField(null=True, blank=True)

    STATUS_NEW = "new"
    STATUS_READY = "ready"
    STATUS_ONGOING = "ongoing"
    STATUS_CLOSED = "closed"
    STATUSES = [
        (STATUS_NEW, _("New")),
        (STATUS_READY, _("Ready")),
        (STATUS_ONGOING, _("Ongoing")),
        (STATUS_CLOSED, _("Closed")),
    ]
    status = models.CharField(max_length=32, choices=STATUSES, default=STATUS_NEW)


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

    active_sprint = models.ForeignKey(Sprint, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        null=True,
        related_name='backlog',
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    @property
    def sprints(self):
        return self.lists

    class Meta(Board.Meta):
        verbose_name = "backlog"
        verbose_name_plural = "backlogs"
