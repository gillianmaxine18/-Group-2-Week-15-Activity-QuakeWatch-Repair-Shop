"""Group tests for QuakeWatch.
"""
import logging
from urllib.parse import parse_qs, urlparse

import pandas as pd
import pytest
import responses

import quakewatch as qw


# ---------------------------------------------------------------------------
# MAXINE: parametrize test (guards defect #3)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("mag, label", [
    (6.0, "Strong"),
    (6.04, "Strong"),
    (6.5, "Strong"),
    (5.9, "Moderate"),
    (6.9, "Strong"),
    (7.0, "Major"),
])
def test_mag_class_around_the_strong_boundary(mag, label):
    assert qw.mag_class(pd.Series([mag])).iloc[0] == label


# ---------------------------------------------------------------------------
# HANS: fake-API test with `responses` (guards defect #5)
# ---------------------------------------------------------------------------
QUERY_URL_PATH = "/fdsnws/event/1/query"
EVENT_MS = 1614556800000          # 2021-03-01 00:00:00 UTC


def _feature(event_id, ms):
    return {"id": event_id,
            "properties": {"mag": 5.5, "place": "Test place", "time": ms, "magType": "mb"},
            "geometry": {"coordinates": [125.0, 8.0, 10.0]}}


@responses.activate
def test_second_load_asks_only_for_newer_events(project):
    url = qw.BASE + QUERY_URL_PATH
    responses.add(responses.GET, url, json={"features": [_feature("fake1", EVENT_MS)]})
    responses.add(responses.GET, url, json={"features": []})

    assert qw.load_new() == 1
    assert qw.load_new() == 0

    assert len(responses.calls) == 2
    second_start = parse_qs(urlparse(responses.calls[1].request.url).query)["starttime"][0]
    assert second_start > "2021-03-01T00:00:00"       # not FIRST_DAY again
    assert qw.read_raw()["id"].tolist() == ["fake1"]


# ---------------------------------------------------------------------------
# ELISHA: caplog test (guards logging for defect #6)
# ---------------------------------------------------------------------------
def test_rejected_rows_produce_a_warning(raw_snapshot, caplog):
    table = raw_snapshot.head(5).copy()
    table.loc[table.index[0], "depth_km"] = -5.0
    with caplog.at_level(logging.WARNING, logger="quakewatch"):
        good, rejected = qw.split_by_contract(table)
    assert len(rejected) == 1 and len(good) == 4
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert "rejected" in warnings[0].getMessage()
    assert "1 of 5" in warnings[0].getMessage()


# ---------------------------------------------------------------------------
# KAYCELYN: run the pipeline twice (guards defects #5 and #1 together)
# ---------------------------------------------------------------------------
def test_two_runs_leave_no_duplicates(project):
    first = qw.run_pipeline()
    second = qw.run_pipeline()
    assert second["new_rows"] == 0
    raw = qw.read_raw()
    assert raw["id"].is_unique
    assert len(raw) == first["new_rows"]
    assert first["rows"] == second["rows"]
