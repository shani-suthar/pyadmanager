import sys
from unittest.mock import Mock

import pytest

from pyadmanager.services import report
from pyadmanager.services.report import (
    ReportClient,
    ReportJob,
    _unwrap_value,
    parse_report_rows,
)

NETWORK_CODE = "123"


def make_page(rows: list[dict]) -> dict:
    return {"rows": rows}


def make_job_metadata(
    job_path: str = "networks/123/reports/5/operations/op1",
    report_path: str = "networks/123/reports/5",
) -> dict:
    return {"name": job_path, "metadata": {"report": report_path}}


class TestUnwrapValue:
    def test_empty_dict_is_null(self):
        assert _unwrap_value({}) is None

    def test_int_value_is_cast_to_int(self):
        value = _unwrap_value({"intValue": "13"})

        assert value == 13
        assert isinstance(value, int)

    def test_double_value_whole_number_is_cast_to_float(self):
        value = _unwrap_value({"doubleValue": 0})

        assert value == 0.0
        assert isinstance(value, float)

    def test_double_value_fraction_stays_float(self):
        assert _unwrap_value({"doubleValue": 0.04}) == 0.04

    def test_string_value_passes_through(self):
        assert _unwrap_value({"stringValue": "House"}) == "House"


class TestParseReportRows:
    def test_builds_dataframe_across_pages_with_correct_dtypes(self):
        pl = pytest.importorskip("polars")

        pages = [
            make_page(
                [
                    {
                        "dimensionValues": [{"intValue": "20240910"}, {"stringValue": "li1"}],
                        "metricValueGroups": [
                            {"primaryValues": [{"doubleValue": 0}, {"intValue": "13"}]}
                        ],
                    }
                ]
            ),
            make_page(
                [
                    {
                        "dimensionValues": [{"intValue": "20240911"}, {"stringValue": "li2"}],
                        "metricValueGroups": [
                            {"primaryValues": [{"doubleValue": 0.04}, {"intValue": "5"}]}
                        ],
                    }
                ]
            ),
        ]

        df = parse_report_rows(pages, ["DATE", "LINE_ITEM_NAME"], ["REVENUE", "IMPRESSIONS"])

        assert df.to_dicts() == [
            {"DATE": 20240910, "LINE_ITEM_NAME": "li1", "REVENUE": 0.0, "IMPRESSIONS": 13},
            {"DATE": 20240911, "LINE_ITEM_NAME": "li2", "REVENUE": 0.04, "IMPRESSIONS": 5},
        ]
        assert df.schema["DATE"] == pl.Int64
        assert df.schema["LINE_ITEM_NAME"] == pl.Utf8
        assert df.schema["REVENUE"] == pl.Float64
        assert df.schema["IMPRESSIONS"] == pl.Int64

    def test_unset_oneof_becomes_null(self):
        pytest.importorskip("polars")

        pages = [
            make_page(
                [
                    {
                        "dimensionValues": [{"intValue": "1"}, {}],
                        "metricValueGroups": [{"primaryValues": [{"intValue": "1"}]}],
                    }
                ]
            )
        ]

        df = parse_report_rows(pages, ["DATE", "LINE_ITEM_NAME"], ["IMPRESSIONS"])

        assert df.to_dicts() == [{"DATE": 1, "LINE_ITEM_NAME": None, "IMPRESSIONS": 1}]

    def test_dimension_count_mismatch_raises(self):
        pytest.importorskip("polars")

        pages = [
            make_page(
                [
                    {
                        "dimensionValues": [{"intValue": "1"}],
                        "metricValueGroups": [{"primaryValues": [{"intValue": "1"}]}],
                    }
                ]
            )
        ]

        with pytest.raises(ValueError, match="dimensionValues"):
            parse_report_rows(pages, ["DATE", "LINE_ITEM_NAME"], ["IMPRESSIONS"])

    def test_metric_count_mismatch_raises(self):
        pytest.importorskip("polars")

        pages = [
            make_page(
                [
                    {
                        "dimensionValues": [{"intValue": "1"}],
                        "metricValueGroups": [
                            {"primaryValues": [{"intValue": "1"}, {"intValue": "2"}]}
                        ],
                    }
                ]
            )
        ]

        with pytest.raises(ValueError, match="metric values"):
            parse_report_rows(pages, ["DATE"], ["IMPRESSIONS"])

    def test_raises_import_error_when_polars_missing(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "polars", None)

        with pytest.raises(ImportError, match=r"pyadmanager\[polars\]"):
            parse_report_rows([], [], [])


class TestReportJobInit:
    def test_paths_are_derived_from_obj_metadata(self, fake_http_client):
        job = ReportJob(make_job_metadata(), NETWORK_CODE, fake_http_client)

        assert job.job_path == "networks/123/reports/5/operations/op1"
        assert job.report_path == "networks/123/reports/5"
        assert job.result_path is None


class TestCheckJobStatus:
    def test_fetches_job_path(self, fake_http_client):
        http_client = fake_http_client
        http_client.fetch.return_value = {"done": True}
        job = ReportJob(make_job_metadata(), NETWORK_CODE, http_client)

        status = job.check_job_status()

        http_client.fetch.assert_called_once_with(job.job_path)
        assert status == {"done": True}


class TestWaitTillComplete:
    def test_polls_until_done(self, monkeypatch, fake_http_client):
        sleep = Mock()
        monkeypatch.setattr("pyadmanager.services.report.time.sleep", sleep)
        http_client = fake_http_client
        http_client.fetch.side_effect = [
            {"done": False},
            {"done": True, "response": {"reportResult": "networks/123/reports/5/results/1"}},
        ]
        job = ReportJob(make_job_metadata(), NETWORK_CODE, http_client)

        job.wait_till_complete(sleep=1.5)

        assert job.result_path == "networks/123/reports/5/results/1"
        sleep.assert_called_once_with(1.5)

    def test_raises_on_error(self, fake_http_client):
        http_client = fake_http_client
        http_client.fetch.return_value = {"error": "boom"}
        job = ReportJob(make_job_metadata(), NETWORK_CODE, http_client)

        with pytest.raises(ValueError, match="boom"):
            job.wait_till_complete()


class TestFetchRows:
    def test_waits_then_fetches_rows(self, monkeypatch, fake_http_client):
        monkeypatch.setattr("pyadmanager.services.report.time.sleep", Mock())
        http_client = fake_http_client
        http_client.fetch.return_value = {
            "done": True,
            "response": {"reportResult": "networks/123/reports/5/results/1"},
        }
        http_client.fetch_report_rows.return_value = [{"rows": []}]
        job = ReportJob(make_job_metadata(), NETWORK_CODE, http_client)

        rows = job.fetch_rows()

        http_client.fetch_report_rows.assert_called_once_with(
            "networks/123/reports/5/results/1:fetchRows"
        )
        assert rows == [{"rows": []}]

    def test_skips_wait_when_result_path_already_known(self, fake_http_client):
        http_client = fake_http_client
        job = ReportJob(make_job_metadata(), NETWORK_CODE, http_client)
        job.result_path = "networks/123/reports/5/results/1"

        job.fetch_rows()

        http_client.fetch.assert_not_called()
        http_client.fetch_report_rows.assert_called_once_with(
            "networks/123/reports/5/results/1:fetchRows"
        )


class TestFetchRowsAsDataframe:
    def test_parses_rows_using_report_definition(self, monkeypatch, fake_http_client):
        http_client = fake_http_client
        job = ReportJob(make_job_metadata(), NETWORK_CODE, http_client)
        pages = [{"rows": []}]
        fetch_rows_mock = Mock(return_value=pages)
        monkeypatch.setattr(job, "fetch_rows", fetch_rows_mock)
        http_client.fetch.return_value = {
            "reportDefinition": {"dimensions": ["DATE"], "metrics": ["IMPRESSIONS"]}
        }
        parsed = object()
        parse_mock = Mock(return_value=parsed)
        monkeypatch.setattr(report, "parse_report_rows", parse_mock)

        result = job.fetch_rows_as_dataframe(sleep=1.0)

        fetch_rows_mock.assert_called_once_with(sleep=1.0)
        http_client.fetch.assert_called_once_with(job.report_path)
        parse_mock.assert_called_once_with(pages, ["DATE"], ["IMPRESSIONS"])
        assert result is parsed


class TestListReports:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        http_client = fake_http_client
        client = ReportClient(NETWORK_CODE, http_client)

        client.list(display_name="test_report_123")

        http_client.fetch_all.assert_called_once_with(
            "networks/123/reports",
            "reports",
            {"pageSize": 1000, "filter": 'displayName = "test_report_123"'},
        )

    def test_report_id_is_resolved_to_full_path(self, fake_http_client):
        http_client = fake_http_client
        client = ReportClient(NETWORK_CODE, http_client)

        client.list(report_id=456)

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/reports/456"'

    def test_report_id_list_is_resolved_to_or_clause(self, fake_http_client):
        http_client = fake_http_client
        client = ReportClient(NETWORK_CODE, http_client)

        client.list(report_id=[1, 2])

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(name = "networks/123/reports/1" OR name = "networks/123/reports/2")'
        )

    def test_all_fields_produce_expected_filter_str_in_order(self, fake_http_client):
        http_client = fake_http_client
        client = ReportClient(NETWORK_CODE, http_client)

        client.list(report_id=456, display_name="test_report_123")

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'name = "networks/123/reports/456" AND displayName = "test_report_123"'
        )

    def test_no_filters_passes_none(self, fake_http_client):
        http_client = fake_http_client
        client = ReportClient(NETWORK_CODE, http_client)

        client.list()

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        http_client = fake_http_client
        http_client.fetch_all.return_value = [{"name": "r1"}]
        client = ReportClient(NETWORK_CODE, http_client)

        assert client.list() == [{"name": "r1"}]


class TestGetReport:
    def test_fetches_by_id_path(self, fake_http_client):
        http_client = fake_http_client
        client = ReportClient(NETWORK_CODE, http_client)

        client.get(456)

        http_client.fetch.assert_called_once_with("networks/123/reports/456")


class TestRunReport:
    def test_posts_to_run_endpoint_and_returns_job(self, fake_http_client):
        http_client = fake_http_client
        http_client.fetch.return_value = make_job_metadata(
            job_path="networks/123/reports/456/operations/op1",
            report_path="networks/123/reports/456",
        )
        client = ReportClient(NETWORK_CODE, http_client)

        job = client.run_report(456)

        http_client.fetch.assert_called_once_with(
            "networks/123/reports/456:run", http_method="POST"
        )
        assert isinstance(job, ReportJob)
        assert job.network_code == "123"
        assert job.http_client is http_client
        assert job.job_path == "networks/123/reports/456/operations/op1"
        assert job.report_path == "networks/123/reports/456"
