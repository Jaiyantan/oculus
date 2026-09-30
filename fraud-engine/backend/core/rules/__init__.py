# Rules package — auto-imports all rule modules so @register_rule decorators fire
from . import velocity_rule  # noqa: F401
from . import amount_rule    # noqa: F401
from . import geo_rule       # noqa: F401
