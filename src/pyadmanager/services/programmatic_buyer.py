"""Filter builder for the ProgrammaticBuyers GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.programmaticBuyers
"""

from ..filters import GAMRestFilters, get_filter_string
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path


class ProgrammaticBuyerClient:
    """Client for the `programmaticBuyers` GAM REST resource."""

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "programmaticBuyers"

    def list(
        self,
        buyer_account_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        parent_account_id: int | list[int] | None = None,
        partner_client_id: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        agency: bool | None = None,
        preferred_deals_enabled: bool | None = None,
        programmatic_guaranteed_enabled: bool | None = None,
        page_size: int = 1000,
    ):
        """List `programmaticBuyers`, paging through every result via `HTTPClient.fetch_all`.

        `buyer_account_id` resolves to `programmaticBuyers/{id}` path(s);
        `parent_account_id` resolves the same way (a buyer's sponsor is
        itself a buyer) — both via `utils.gam_obj_id_path` before filtering.
        Fields left as `None` are omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        buyer_account_id_str = gam_obj_id_path(
            buyer_account_id, self.network_code, self._gam_obj_type
        )
        parent_account_id_str = gam_obj_id_path(
            parent_account_id, self.network_code, self._gam_obj_type
        )

        filter_list = [
            GAMRestFilters.id_based_filter("name", buyer_account_id_str),
            GAMRestFilters.text_filter("displayName", display_name),
            GAMRestFilters.id_based_filter("parentAccountId", parent_account_id_str),
            GAMRestFilters.text_filter("partnerClientId", partner_client_id),
            GAMRestFilters.boolean_filter("agency", agency),
            GAMRestFilters.boolean_filter("preferredDealsEnabled", preferred_deals_enabled),
            GAMRestFilters.boolean_filter(
                "programmaticGuaranteedEnabled", programmatic_guaranteed_enabled
            ),
        ]

        filter_str = get_filter_string(filter_list)

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get(self, buyer_account_id: int):
        """Fetch a single `programmaticBuyer` by numeric account id."""
        endpoint = gam_obj_id_path(buyer_account_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
