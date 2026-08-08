from datetime import UTC, datetime

from pyadmanager.filters import BaseRestFilter, GAMRestFilters


class TestTextFilter:
    def test_single_string(self):
        assert GAMRestFilters.text_filter("status", "ACTIVE") == 'status = "ACTIVE"'

    def test_list_of_strings(self):
        assert (
            GAMRestFilters.text_filter("status", ["ACTIVE", "INACTIVE"])
            == '(status = "ACTIVE" OR status = "INACTIVE")'
        )

    def test_contains_tuple(self):
        assert (
            GAMRestFilters.text_filter("displayName", ("foo", "CONTAINS"))
            == 'displayName = "*foo*"'
        )

    def test_startwith_tuple(self):
        assert (
            GAMRestFilters.text_filter("displayName", ("foo", "STARTWITH"))
            == 'displayName = "foo*"'
        )

    def test_endwith_tuple(self):
        assert (
            GAMRestFilters.text_filter("displayName", ("foo", "ENDWITH")) == 'displayName = "*foo"'
        )

    def test_is_null_tuple(self):
        assert GAMRestFilters.text_filter("displayName", ("", "IS_NULL")) == "displayName IS NULL"

    def test_none_returns_empty_string(self):
        assert GAMRestFilters.text_filter("status", None) == ""


class TestIdBasedFilter:
    def test_single_id_path_is_double_quoted(self):
        assert (
            GAMRestFilters.id_based_filter("name", "networks/123/lineItems/456")
            == 'name = "networks/123/lineItems/456"'
        )

    def test_list_of_id_paths(self):
        assert GAMRestFilters.id_based_filter("name", ["a", "b"]) == '(name = "a" OR name = "b")'

    def test_none_returns_empty_string(self):
        assert GAMRestFilters.id_based_filter("name", None) == ""


class TestNumberFilter:
    def test_single_number_is_bare(self):
        assert GAMRestFilters.number_filter("priority", 5) == "priority = 5"

    def test_comparison_tuple(self):
        assert GAMRestFilters.number_filter("priority", (5, "GT_EQ")) == "priority >= 5"

    def test_list_of_numbers_is_bare(self):
        assert GAMRestFilters.number_filter("priority", [1, 2]) == "(priority = 1 OR priority = 2)"

    def test_none_returns_empty_string(self):
        assert GAMRestFilters.number_filter("priority", None) == ""


class TestIdFilter:
    def test_single_id_is_bare(self):
        assert GAMRestFilters.id_filter("key.id", 5) == "key.id = 5"

    def test_not_equal_to_tuple(self):
        assert GAMRestFilters.id_filter("key.id", (5, "NOT_EQUAL_TO")) == "key.id != 5"

    def test_none_returns_empty_string(self):
        assert GAMRestFilters.id_filter("key.id", None) == ""


class TestBooleanFilter:
    def test_true_is_bare_lowercase(self):
        assert GAMRestFilters.boolean_filter("archived", True) == "archived = true"

    def test_false_is_bare_lowercase(self):
        assert GAMRestFilters.boolean_filter("archived", False) == "archived = false"

    def test_none_returns_empty_string(self):
        assert GAMRestFilters.boolean_filter("archived", None) == ""


class TestDateFilter:
    def test_single_datetime_is_double_quoted_rfc3339(self):
        dt = datetime(2025, 1, 1, tzinfo=UTC)
        assert (
            GAMRestFilters.date_filter("updateTime", dt)
            == 'updateTime = "2025-01-01T00:00:00+00:00"'
        )

    def test_naive_datetime_is_treated_as_utc(self):
        dt = datetime(2025, 1, 1)  # noqa: DTZ001
        assert (
            GAMRestFilters.date_filter("updateTime", dt)
            == 'updateTime = "2025-01-01T00:00:00+00:00"'
        )

    def test_comparison_tuple(self):
        dt = datetime(2025, 1, 1, tzinfo=UTC)
        assert (
            GAMRestFilters.date_filter("updateTime", (dt, "GT_EQ"))
            == 'updateTime >= "2025-01-01T00:00:00+00:00"'
        )

    def test_none_returns_empty_string(self):
        assert GAMRestFilters.date_filter("updateTime", None) == ""


class TestBaseRestFilter:
    def test_joins_non_empty_clauses_with_and(self):
        class FakeFilter(BaseRestFilter):
            def _build_filter_list(self):
                return ['status = "ACTIVE"', "", 'name = "foo"']

        assert FakeFilter().get_filter_string() == 'status = "ACTIVE" AND name = "foo"'

    def test_all_empty_clauses_returns_none(self):
        class FakeFilter(BaseRestFilter):
            def _build_filter_list(self):
                return ["", ""]

        assert FakeFilter().get_filter_string() is None
