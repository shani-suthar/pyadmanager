"""Per-GAM-resource clients, one module per resource (custom targeting, line items, reports).

Each module follows the same shape: `Literal` type aliases for the
resource's enum fields, a `*Filter(BaseRestFilter)` for building its filter
string, and a `*Client` with `list_*`/`get_*` methods built on the shared
`HTTPClient`. `GAMClient` exposes one of each as a cached property.
"""

from .custom_targeting import CustomTargetingClient
from .line_item import LineItemClient
from .report import ReportClient

__all__ = ["CustomTargetingClient", "LineItemClient", "ReportClient"]
