from .resources import create_resources
from .tools import create_tools


def create_protocol(mcp):
    """Initialize the protocol with tools and resources."""
    create_tools(mcp)  # Register all tools defined in protocol/tools.py
    create_resources(mcp)  # Register all resources defined in protocol/resources.py
