# Diagram Agent API

**Python 48-hour job interview assignment**

An async, containerized,  stateless Python API service that generates infrastructure diagrams from natural language descriptions using LLM agents and the Python [`diagrams`](https://diagrams.mingrammer.com/) package.

## Quick Start

### Prerequisites

- **Docker Desktop** (recommended) or Docker + Docker Compose
- **Gemini API Key** from Google AI Studio

### Installation

1. **Clone and setup**:
   ```bash
   git clone https://github.com/Yair-lahad/nlp-diagram-creator.git
   cd nlp-diagram-creator
   ```

2. **Configure environment**:
   
   Ensure your `.env` file contains the required variables with actual API key:
   ```
   GEMINI_API_KEY=<your_actual_api_key_here>
   LLM_PROVIDER=gemini
   ```

3. **Run with Docker**:
   ```bash
   docker-compose up --build
   ```

   You should see in the terminal output:
   ```
   api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```

Note: The API only provides endpoints, not a web interface. You cannot browse to localhost:8000 directly in a browser.

### Usage Example (input and output)

Send a POST request to `/diagram` with a natural language description input:

**Using Postman**:
- Method: `POST`
- URL: `http://localhost:8000/diagram`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "description": "Create a diagram showing a basic web application with an Application Load Balancer, two EC2 instances for the web servers, and an RDS database for storage. The web servers should be in a cluster named Web Tier."
}
```
Postman will generate a preview output that matches the expected PNG below, with the possibility to download it.

**Using curl on another Terminal window on project directory**:
```bash
curl -X POST "http://localhost:8000/diagram" -H "Content-Type: application/json" -d "{\"description\": \"Create a diagram showing a basic web application with an Application Load Balancer, two EC2 instances for the web servers, and an RDS database for storage. The web servers should be in a cluster named Web Tier.\"}" --output diagram.png
```

Curl will save an output "diagram.png" file to your local code directory.

**Expected Output**: The API returns a PNG image showing the architecture diagram with AWS icons and proper connections, similar to this:

![image](https://github.com/user-attachments/assets/2ce96bd8-ccc0-459e-8082-696328e231d2)


## Architecture

### Agent Orchestration

The system uses a **tool-based agent architecture** where the LLM doesn't directly interact with the `diagrams` package:

```
User Input → API → Dispatcher → Agent → LLM Client → Parser → Generator → Tools → Diagram
```

**Key Design Principles**:

- **Agent Orchestration**: Single agent coordinates the entire pipeline with architecture designed to scale to multi-agent systems
- **LLM as Tool Caller**: The LLM receives only tool schemas and generates structured tool calls (JSON), never seeing actual implementation code
- **Separation of Concerns**: Each layer has a single responsibility - API handles HTTP, agents orchestrate, tools execute
- **Stateless Operation**: Each request is independent with no session or database storage

### Core Components

- **`app/api/`**: API routes and HTTP request handling
- **`app/agent/`**: Agent orchestration layer that coordinates the generation pipeline
- **`app/core/`**: Core system logic including:
  - **Dispatcher**: Request routing layer that separates API from logic
  - **Tools**: Wrapper around `diagrams` package that Agent handles.
  - **Models**: Centralized data structures and prompt templates
  - **Parsers**: Convert LLM JSON output to structured data
  - **Generators**: Execute parsed tool calls to create diagrams using Tools.
- **`app/llm/`**: LLM client implementations (currently Gemini with modular adaptable base interface)

**LLM Client Interaction**:

*Prompt example sent to LLM*:
```
You are a diagram generation assistant...
IMPORTANT RULES:
- You must ONLY use the tools provided
- Use only these node_type values: ec2, rds, elb, api_gateway, sqs, cloudwatch
- Do NOT reference Python code or diagrams package directly

Available tools:
- create_node: Create a node/component
- connect_nodes: Create connection between nodes  
- render_diagram: Generate final diagram

User request: Create a load balancer with two web servers
```

*Raw response example from LLM*:
```json
[
  {"tool": "create_node", "args": {"name": "Load Balancer", "node_type": "elb"}},
  {"tool": "create_node", "args": {"name": "Web Server 1", "node_type": "ec2"}},
  {"tool": "connect_nodes", "args": {"from_node": "Load Balancer", "to_node": "Web Server 1"}},
  {"tool": "render_diagram", "args": {"title": "Load Balanced Web Servers"}}
]
```

### Supported Node Types

- `ec2` - AWS EC2 instances
- `rds` - AWS RDS databases  
- `elb` - AWS Load Balancers
- `api_gateway` - AWS API Gateway
- `sqs` - AWS SQS queues
- `cloudwatch` - AWS CloudWatch monitoring

Note: Currently 6 types, easily scalable by adding types directly in central core models.py file.

### Local Development (without Docker) - NOT RECOMMENDED!

**Note**: Local development may require additional system dependencies such as Conda env and Graphviz and is not fully tested.

### Environment Variables

- `GEMINI_API_KEY`: Required - Your Google Gemini API key
- `LLM_PROVIDER`: Optional - Defaults to "gemini"

```bash
# Install UV package manager on current conda env
pip install uv

# Install dependencies
uv sync

# Run locally (may require additional setup)
uv run --env-file .env uvicorn app.main:app --reload

# run the example from Postman/ curl as you wish
curl -X POST "http://localhost:8000/diagram" -H "Content-Type: application/json" -d "{\"description\":\"Create a load balancer with one web server\"}" --output simple.png
```




# Considerations and Limitations

- System built modular and could easily scaled to multi Agents solution
- Currently supports AWS infrastructure components only
- Requires active internet connection for LLM API calls
- Generated diagrams are temporary files
- Further testing and error handling can be added as project grows

