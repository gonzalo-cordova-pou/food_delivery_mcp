import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from protocol import create_protocol

load_dotenv()

# Read environment variables for server configuration
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "FoodieApp Assistant")
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", 8050))


# Initialize the FastMCP server with a human-readable name.
# This name will be visible in client applications like Claude Desktop.
mcp = FastMCP(
    name=MCP_SERVER_NAME,
    host=MCP_SERVER_HOST,
    port=MCP_SERVER_PORT,
    dependencies=["google-cloud-firestore", "firebase-admin"],
)

create_protocol(mcp)  # Register tools and resources defined in protocol module


if __name__ == "__main__":
    try:
        # mcp.run() starts the server, typically using the stdio transport by default,
        # which is ideal for local development with clients like Claude Desktop.
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error starting MCP server: {e}", file=sys.stderr)
