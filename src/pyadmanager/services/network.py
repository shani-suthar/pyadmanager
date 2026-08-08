"""Client for the Networks GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks
"""

from ..http_client import HTTPClient


class NetworkClient:
    """Client for the `networks` GAM REST resource.

    Unlike every other resource client, `networks` is a top-level resource
    (`networks/{networkCode}`, not `networks/{networkCode}/{gam_obj_type}/...`)
    with no documented filterable fields — `list_networks` simply returns
    every network the caller's credentials have access to, so there's no
    matching `NetworkFilter` class the way other resources have one.
    """

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "networks"

    def list_networks(self, page_size: int = 1000):
        """List every `network` the caller's credentials have access to.

        No filter fields are documented for this resource, so unlike other
        `list_*` methods there's no `filter` query param to build.
        """
        params = {"pageSize": page_size}
        return self.http_client.fetch_all(self._gam_obj_type, self._gam_obj_type, params)

    def get_network(self, network_code: str | int | None = None):
        """Fetch a single `network` by code, defaulting to this client's own `network_code`.

        Pass an explicit `network_code` to look up a *different* network
        than the one this client was constructed for (e.g. one discovered
        via `list_networks`). Builds the path directly rather than via
        `utils.gam_obj_id_path`/`gam_obj_path`, since those assume the
        `networks/{code}/{gam_obj_type}/{id}` shape every other resource
        uses — `networks` itself has no such nesting.
        """
        code = str(network_code) if network_code is not None else self.network_code
        endpoint = f"networks/{code}"
        return self.http_client.fetch(endpoint)
