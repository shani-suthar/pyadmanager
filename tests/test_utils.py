from pyadmanager.utils import gam_obj_id_path, gam_obj_path


class TestGamObjIdPath:
    def test_single_int(self):
        assert gam_obj_id_path(456, "123", "lineItems") == "networks/123/lineItems/456"

    def test_list_of_ints(self):
        assert gam_obj_id_path([1, 2], "123", "lineItems") == [
            "networks/123/lineItems/1",
            "networks/123/lineItems/2",
        ]

    def test_empty_list(self):
        assert gam_obj_id_path([], "123", "lineItems") == []

    def test_none_returns_none(self):
        assert gam_obj_id_path(None, "123", "lineItems") is None


class TestGamObjPath:
    def test_builds_path(self):
        assert gam_obj_path("123", "lineItems") == "networks/123/lineItems"
