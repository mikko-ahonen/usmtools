import logging

from django_components import component

from workflows.tenant import current_tenant_id
from stats.models import Dataset

@component.register("burndown")
class Burndown(component.Component):
    template_name = "burndown/burndown.html"

    def get_context_data(self, **kwargs):

        index = kwargs["index"]

        if "tenant_id" not in kwargs:
            raise ValueError("tenant_id required")

        if "object" not in kwargs:
            raise ValueError("object required")

        try:
            burndown_ds = Dataset.by_object(kwargs["tenant_id"], kwargs["object"])
            ideal_ds = Dataset.by_object(kwargs["tenant_id"], burndown_ds)
        except Dataset.DoesNotExist:
            burndown_ds = None
            ideal_ds = None

        return {
            "index": str(index),
            "burndown_dataset": burndown_ds,
            "ideal_dataset": ideal_ds,
            "legends": self.as_chartjs_legends(ideal_ds) if ideal_ds else None,
            "burndown_data": self.as_chartjs_data(burndown_ds) if ideal_ds else None,
            "ideal_data": self.as_chartjs_data(ideal_ds) if ideal_ds else None,
        }

    def as_chartjs_data(self, dataset):
        return [float(dp.value) for dp in dataset.datapoint_set(manager='unscoped').order_by('date')]

    def as_chartjs_legends(self, dataset):
        return [dp.date for dp in dataset.datapoint_set(manager='unscoped').order_by('date')]

    class Media:
        js = "burndown/burndown.js"
