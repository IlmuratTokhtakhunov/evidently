import json
from typing import List

import pandas as pd
import pytest

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.base_metric import TResult
from evidently.metric_results import Distribution
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.report import Report


class MockMetricResult(MetricResult):
    class Config:
        dict_exclude_fields = {"series", "distribution"}

    value: str
    series: pd.Series
    distribution: Distribution


class MockMetric(Metric[MockMetricResult]):
    def calculate(self, data: InputData) -> MockMetricResult:
        return MockMetricResult(value="a", series=pd.Series([0]), distribution=Distribution(x=[1, 1], y=[0, 0]))


@default_renderer(wrap_type=MockMetric)
class MockMetricRenderer(MetricRenderer):
    def render_html(self, obj) -> List[BaseWidgetInfo]:
        # todo?
        raise NotImplementedError


@pytest.fixture
def report():
    report = Report(metrics=[MockMetric()])
    report.run(reference_data=pd.DataFrame(), current_data=pd.DataFrame())
    return report


def test_as_dict(report: Report):
    assert report.as_dict() == {"metrics": [{"metric": "MockMetric", "result": {"value": "a"}}]}
    include_series = report.as_dict(include={"MockMetric": {"value", "series"}})
    assert "series" in include_series["metrics"][0]["result"]
    assert (pd.Series([0]) == include_series["metrics"][0]["result"]["series"]).all()


def test_json(report: Report):
    default = json.loads(report.json())["metrics"]
    assert default == [{"metric": "MockMetric", "result": {"value": "a"}}]

    include_series = json.loads(report.json(include={"MockMetric": {"value", "series"}}))["metrics"]
    assert include_series == [{"metric": "MockMetric", "result": {"value": "a", "series": [0]}}]
