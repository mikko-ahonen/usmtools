import django_filters
from django import forms
from django.shortcuts import get_object_or_404

from crispy_forms.helper import FormHelper

from compliances.models import Project
from projects.models import Sprint, Release


def sprint_teams(request):
    if request is None:
        return Team.objects.none()

    kwargs = request.resolver_match.kwargs
    
    tenant_id = kwargs.get('tenant_id', None)

    if not tenant_id:
        return Team.objects.none()

    project_id = kwargs.get('pk', None)

    if not project_id:
        return Team.objects.none()

    project = get_object_or_404(Project, id=project_id)

    if not project_id:
        return Team.objects.none()

    return Team.unscoped.filter(tenant_id=tenant_id, project_id=project.id)


class ReleaseFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Release.STATUSES)

    class Meta:
        model = Release
        fields = ['status' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.form_tag = False


class SprintFilter(django_filters.FilterSet):
    team = django_filters.ModelChoiceFilter(queryset=sprint_teams)

    class Meta:
        model = Sprint
        fields = ['team' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.form_tag = False
        #self.form.helper.form_method = 'get'
        #self.form.helper.layout = Layout(
        #    Row(
        #        Column('name', css_class='form-group col-md-6 mb-0'),
        #        Column('category', css_class='form-group col-md-6 mb-0'),
        #    ),
        #)
        #self.form.helper.add_input(Submit('submit', 'Apply Filters'))
