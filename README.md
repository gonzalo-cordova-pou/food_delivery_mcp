# Local Model Context Protocol Server for a Food Delivery Application

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/release/python-3100/) <a href="https://github.com/kefranabg/readme-md-generator/blob/master/LICENSE">
![](https://badge.mcpx.dev?type=server 'MCP Server')
[![Model Context Protocol](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-orange)](https://modelcontextprotocol.io/introduction)
[![Firebase](https://img.shields.io/badge/Firebase-039BE5?logo=Firebase&logoColor=white)](#)

## Demo

### Are you hungry? Ask for the restaurant menu!

![
Asking for food.
](./docs/images/demo1.png)

### Let the agent order for you!

![alt text](./docs/images/demo2.png)

### Check the status of your order!

![alt text](./docs/images/demo3.png)


## Code structure

An effective directory layout for the food delivery MCP server is as follows:

```
food-delivery-mcp/
├──.venv/                   # The isolated Python virtual environment
├──.env                     # Secure storage for environment variables
├── data_models/
│   └── models.py           # The dataclasses provided for the application
├── db/
│   └── firestore_client.py # All database interaction logic
├── protocol/
│   ├── __init__.py         # Initializes the protocol package
│   ├── resources.py        # Defines the MCP Resources for the application
│   └── tools.py            # Defines the MCP Tools for the application
├── server.py               # The main FastMCP server implementation
├── pyproject.toml          # Project metadata and dependencies
├── requirements.txt        # List of dependencies for the project
└── README.md               # Project documentation
```

This structure intentionally isolates distinct logical components. The database interaction logic is encapsulated within the db/ directory, completely separate from the MCP server definition in server.py. This architectural decision is pivotal. It allows the server to act as a clean orchestration layer, defining the Tools and Resources available to the AI agent and delegating the underlying data operations to the firestore_client module. This separation makes each component independently testable and easier to reason about, a significant advantage when time is of the essence.

## Database client

For this project we use Firestore as the database. The `db/firestore_client.py` module encapsulates all interactions with Firestore, providing a clean interface for the server to use. This separation of concerns allows for easier testing and maintenance.

### Mapping Application Logic to MCP Primitives: Thinking in AI Terms

The MCP specification defines two primary ways for a server to expose capabilities: Resources and Tools. The distinction between them is one of the most important architectural concepts in the protocol, and getting it right is key to building an effective server.

Resources are defined as application-controlled, read-only data sources. They are meant to provide context to the LLM. Think of them as analogous to    

GET endpoints in a traditional REST API. They retrieve information without causing any side effects or state changes. The client application (the "host") typically decides when and how to fetch these resources to inform the model.   

Tools are defined as model-controlled functions that the LLM can decide to execute to perform an action. They are analogous to    

POST, PUT, or DELETE endpoints in a REST API. They are expected to perform computations and can have side effects, such as creating or modifying data in a database. The AI agent itself determines that a tool needs to be called based on the user's request, and for security, the user should always be prompted for confirmation before a sensitive tool is executed.   

For the food delivery app, the features can be mapped to MCP primitives as follows:

| Feature                     | MCP Primitive | Justification                                                                 | Example Natural Language Invocation
|-----------------------------|----------------|-------------------------------------------------------------------------------|------------------------------------------------------------|
| Search for restaurants   | Tool           | This is an active search operation that requires parameters (e.g., cuisine, rating) and performs a filtered query against the database. The LLM decides when to perform this action based on a user's request to find something specific. | "Find me Italian restaurants with a rating above 4 stars" |
| View a restaurant's menu | Resource       | This is a pure, read-only data retrieval for a specific entity (a restaurant). Once a restaurant is identified, the host application can fetch its menu as context for the LLM without the LLM needing to perform an "action". | (After user selects a restaurant) The client fetches the resource at `foodapp://restaurants/{id}/menu` |
| Place an order            | Tool           | This is the quintessential action. It has significant side effects: it creates a new Order document in Firestore and initiates a real-world process. It requires explicit invocation and user confirmation. | "Order a margherita pizza from Pizza Palace." |
| Check order status        | Tool           | While this is a read operation, it's an action taken to retrieve a specific, dynamic piece of information for the user based on a unique identifier (the order ID). It's a direct request for the server to do something. | "What is the status of my last order?" |
| List all available cuisines | Resource       | This involves retrieving a list of relatively static, descriptive data. It's useful context for the LLM to know the possible values it can use for the cuisine parameter in the search_restaurants tool. | "What types of food can I order?" |


