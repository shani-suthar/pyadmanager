"""Per-GAM-resource clients, one module per resource (custom targeting, line items, reports, ...).

Each module follows the same shape: `Literal` type aliases for the
resource's enum fields, and a `*Client` with `list_*`/`get_*` methods built
on the shared `HTTPClient` — `list_*` builds its filter clauses inline via
`filters.GAMRestFilters` and joins them with `filters.get_filter_string()`.
`GAMClient` exposes one of each as a cached property. A few resources
(`networks`, `users`) don't support the full `list_*`+`get_*` shape — see
their modules for what's different and why.
"""

from .ad_unit import AdUnitClient
from .custom_targeting import CustomTargetingClient
from .line_item import LineItemClient
from .network import NetworkClient
from .order import OrderClient
from .placement import PlacementClient
from .private_auction import PrivateAuctionClient
from .private_auction_deal import PrivateAuctionDealClient
from .programmatic_buyer import ProgrammaticBuyerClient
from .report import ReportClient
from .role import RoleClient
from .user import UserClient

__all__ = [
    "AdUnitClient",
    "CustomTargetingClient",
    "LineItemClient",
    "NetworkClient",
    "OrderClient",
    "PlacementClient",
    "PrivateAuctionClient",
    "PrivateAuctionDealClient",
    "ProgrammaticBuyerClient",
    "ReportClient",
    "RoleClient",
    "UserClient",
]
