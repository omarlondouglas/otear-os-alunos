"""Stable product capabilities.

Capabilities are the product-level skills used by orchestrators, workflows,
and agents. Existing tools can remain in their legacy modules while new code
depends on this smaller conceptual surface.
"""

from app.capabilities.registry import CAPABILITIES, Capability, get_capability, list_capabilities

__all__ = ["CAPABILITIES", "Capability", "get_capability", "list_capabilities"]
