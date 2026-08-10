"""Client for the Users GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.users
"""

from ..http_client import HTTPClient
from ..utils import gam_obj_id_path


class UserClient:
    """Client for the `users` GAM REST resource.

    Only `get` is documented for this resource (no `list`), so unlike other
    resources there's no matching `UserFilter`/`list` method — a user must
    already be known by id.
    """

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "users"

    def get(self, user_id: int):
        """Fetch a single `user` by numeric id."""
        endpoint = gam_obj_id_path(user_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
