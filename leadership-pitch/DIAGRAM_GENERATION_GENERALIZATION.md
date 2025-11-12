# Generalizing Diagram Generation for mars-core

## Executive Summary

MARS has developed robust diagram generation capabilities for the Leadership Brief, including mermaid diagram conversion, PlantUML integration, and documentation pipeline enhancements. These capabilities should be generalized and integrated into mars-core to benefit all MARS components and research projects.

## Current State

### Existing Diagram Capabilities

1. **PlantUML Service** (`modules/services/plantuml/`)
   - Port: 8080
   - Supports: Sequence, Activity, Class, Component, State diagrams
   - Architecture: Docker container running PlantUML server
   - Usage: HTTP API for generating diagrams from PlantUML syntax

2. **Mermaid Integration** (Leadership Brief)
   - Tools: mermaid-cli (mmdc), mermaid-filter (pandoc)
   - Supports: Flowcharts, Sequence, State, Gantt, Git graphs
   - Architecture: Build-time generation via Node.js CLI
   - Usage: Manual scripts in `leadership-pitch/diagrams/`

3. **Documentation Pipeline** (Leadership Brief)
   - Tools: pandoc, lualatex, custom conversion scripts
   - Supports: Markdown → PDF with embedded diagrams
   - Architecture: Shell scripts + Python converters
   - Usage: `make_pdf.sh`, `convert_all_diagrams.py`

### Current Limitations

1. **Fragmentation**: Diagram tools scattered across:
   - PlantUML service (containerized)
   - Mermaid CLI (Node.js installed globally)
   - Conversion scripts (ad-hoc Python scripts)

2. **No Programmatic API**: Can't generate diagrams from Python code or agents

3. **Limited Caching**: No centralized cache for generated diagrams

4. **No Standardization**: Each component reinvents diagram generation

5. **Manual Process**: Diagrams must be manually created and converted

## Proposed Architecture

### Option 1: Unified Diagram Service (Recommended)

Create a new service: `modules/services/diagram-generator/`

```
modules/services/diagram-generator/
├── Dockerfile
├── docker-compose.fragment.yml
├── README.md
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── routes.py            # API endpoints
│   │   └── models.py            # Pydantic models
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── base.py              # Base generator interface
│   │   ├── mermaid.py           # Mermaid generator
│   │   ├── plantuml.py          # PlantUML generator (delegates to plantuml service)
│   │   ├── graphviz.py          # GraphViz generator
│   │   └── ascii.py             # ASCII art generator
│   ├── cache/
│   │   ├── __init__.py
│   │   └── manager.py           # Caching logic
│   └── utils/
│       ├── __init__.py
│       └── validators.py        # Input validation
├── tests/
│   ├── test_api.py
│   ├── test_generators.py
│   └── test_cache.py
└── docs/
    ├── API.md
    └── USAGE.md
```

**Key Features**:
- FastAPI REST API for diagram generation
- Support for multiple diagram formats (mermaid, plantuml, graphviz, ascii)
- Redis-based caching (content hash → generated image)
- Async generation for better performance
- Health checks and metrics

**API Endpoints**:
```python
POST /api/v1/diagrams/generate
Request:
{
  "format": "mermaid",  # or "plantuml", "graphviz", "ascii"
  "content": "graph TD\n  A --> B",
  "output_format": "pdf",  # or "png", "svg"
  "options": {
    "width": 800,
    "theme": "default",
    "background": "transparent"
  }
}

Response:
{
  "diagram_id": "sha256:abc123...",
  "format": "mermaid",
  "output_format": "pdf",
  "url": "/api/v1/diagrams/abc123/diagram.pdf",
  "cache_hit": false,
  "generated_at": "2025-11-12T04:20:00Z"
}

GET /api/v1/diagrams/{diagram_id}/{filename}
# Returns the generated diagram file
```

### Option 2: Core Library (Alternative)

Create a library: `core/src/diagrams/`

```python
from mars.diagrams import DiagramGenerator

# Generate a diagram
gen = DiagramGenerator()
result = gen.generate(
    format="mermaid",
    content="graph TD\n  A --> B",
    output_format="pdf",
    output_path="diagram.pdf"
)

# With caching
result = gen.generate(
    format="mermaid",
    content="graph TD\n  A --> B",
    output_format="pdf",
    cache=True
)
```

**Pros**:
- Simpler to use from Python code
- No HTTP overhead
- Integrated directly into core

**Cons**:
- Requires mermaid-cli/plantuml installed locally
- No centralized caching across processes
- Harder to scale independently

### Option 3: Hybrid Approach (Best of Both Worlds)

Combine Options 1 and 2:
- **Service** (`diagram-generator` service): Centralized generation and caching
- **Library** (`core/src/diagrams/`): Python client for the service

```python
from mars.diagrams import DiagramClient

# Client auto-discovers diagram-generator service via Docker DNS
client = DiagramClient()

# Generate a diagram (uses HTTP API internally)
result = await client.generate(
    format="mermaid",
    content="graph TD\n  A --> B",
    output_format="pdf"
)

# Diagram is cached on the service, subsequent requests are fast
```

## Integration Points

### 1. ADR Documentation Workflow

```python
# In docczar agent or ADR authoring tool
from mars.diagrams import DiagramClient

async def generate_adr_architecture_diagram(adr_id: str, architecture_spec: dict):
    client = DiagramClient()

    # Generate mermaid syntax from architecture spec
    mermaid_content = generate_mermaid_from_spec(architecture_spec)

    # Generate diagram
    result = await client.generate(
        format="mermaid",
        content=mermaid_content,
        output_format="svg",
        options={"theme": "base"}
    )

    # Save to ADR directory
    diagram_path = f"docs/wiki/adr/{adr_id}/architecture.svg"
    save_diagram(result.url, diagram_path)

    return diagram_path
```

### 2. Agent Communication Visualizations

```python
# In orchestrator agent
from mars.diagrams import DiagramClient

async def visualize_agent_workflow(workflow: LangGraphWorkflow):
    client = DiagramClient()

    # Convert LangGraph workflow to mermaid
    mermaid_content = workflow.to_mermaid()

    # Generate diagram
    result = await client.generate(
        format="mermaid",
        content=mermaid_content,
        output_format="svg"
    )

    # Store in MLflow as artifact
    mlflow.log_artifact(result.url, "workflow_diagram.svg")
```

### 3. Provenance Tracking Visualization

```python
# In provenance-logger agent
from mars.diagrams import DiagramClient

async def generate_provenance_graph(experiment_id: str):
    client = DiagramClient()

    # Query Neo4j for provenance relationships
    provenance_data = query_provenance_graph(experiment_id)

    # Generate GraphViz DOT syntax
    dot_content = generate_dot_from_provenance(provenance_data)

    # Generate diagram
    result = await client.generate(
        format="graphviz",
        content=dot_content,
        output_format="png"
    )

    return result.url
```

### 4. Documentation Generation

```python
# In documentation build pipeline
from mars.diagrams import DiagramClient

async def process_markdown_with_diagrams(markdown_path: str, output_path: str):
    """Convert markdown with embedded diagram code blocks to PDF."""
    client = DiagramClient()

    # Parse markdown for diagram blocks
    diagrams = extract_diagram_blocks(markdown_path)

    # Generate all diagrams in parallel
    tasks = [
        client.generate(
            format=diagram.format,
            content=diagram.content,
            output_format="pdf"
        )
        for diagram in diagrams
    ]
    results = await asyncio.gather(*tasks)

    # Replace diagram blocks with image references
    markdown_with_images = replace_diagrams_with_images(
        markdown_path,
        diagrams,
        results
    )

    # Convert to PDF with pandoc
    generate_pdf(markdown_with_images, output_path)
```

## Implementation Plan

### Phase 1: Core Service (Week 1-2)
- [ ] Create `modules/services/diagram-generator/` structure
- [ ] Implement FastAPI application with health checks
- [ ] Implement Mermaid generator (delegate to mermaid-cli)
- [ ] Implement PlantUML generator (delegate to existing service)
- [ ] Add Docker container with Node.js + Python
- [ ] Add redis for caching
- [ ] Write unit tests (80% coverage target)

### Phase 2: Python Client Library (Week 2-3)
- [ ] Create `core/src/mars_framework/diagrams/` module
- [ ] Implement DiagramClient class
- [ ] Add async/sync API support
- [ ] Add service discovery (Docker DNS)
- [ ] Write integration tests
- [ ] Document API usage

### Phase 3: Advanced Generators (Week 3-4)
- [ ] Add GraphViz generator
- [ ] Add ASCII art generator (using graph-easy or similar)
- [ ] Add D3.js generator for interactive diagrams
- [ ] Add theme support (custom colors, fonts)
- [ ] Add diagram validation

### Phase 4: Documentation Integration (Week 4-5)
- [ ] Create markdown preprocessor tool
- [ ] Integrate with ADR authoring workflow
- [ ] Create template gallery (common diagram patterns)
- [ ] Add CLI tool: `mars diagram generate <file.mmd>`
- [ ] Document best practices

### Phase 5: Agent Integration (Week 5-6)
- [ ] Integrate with orchestrator for workflow visualization
- [ ] Integrate with provenance-logger for graph generation
- [ ] Integrate with docczar for documentation diagrams
- [ ] Add OpenTelemetry tracing
- [ ] Performance optimization

## Technical Specifications

### Docker Compose Fragment

```yaml
# modules/services/diagram-generator/docker-compose.fragment.yml
services:
  diagram-generator:
    build: modules/services/diagram-generator
    container_name: ${COMPOSE_PROJECT_NAME:-mars}-diagram-generator
    ports:
      - "8081:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - PLANTUML_URL=http://plantuml:8080
      - LOG_LEVEL=${LOG_LEVEL:-info}
    volumes:
      - diagram-cache:/app/cache
    networks:
      - mars-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      - "mars.service=diagram-generator"
      - "mars.healthz.path=/healthz"
      - "mars.metrics.path=/metrics"

  redis:
    image: redis:7-alpine
    container_name: ${COMPOSE_PROJECT_NAME:-mars}-redis
    volumes:
      - redis-data:/data
    networks:
      - mars-network

volumes:
  diagram-cache:
  redis-data:
```

### Python API Example

```python
# core/src/mars_framework/diagrams/client.py
from typing import Literal, Optional
from pydantic import BaseModel
import httpx

DiagramFormat = Literal["mermaid", "plantuml", "graphviz", "ascii"]
OutputFormat = Literal["pdf", "png", "svg"]

class DiagramRequest(BaseModel):
    format: DiagramFormat
    content: str
    output_format: OutputFormat = "svg"
    options: Optional[dict] = None

class DiagramResult(BaseModel):
    diagram_id: str
    format: DiagramFormat
    output_format: OutputFormat
    url: str
    cache_hit: bool
    generated_at: str

class DiagramClient:
    def __init__(self, base_url: str = "http://diagram-generator:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def generate(
        self,
        format: DiagramFormat,
        content: str,
        output_format: OutputFormat = "svg",
        options: Optional[dict] = None
    ) -> DiagramResult:
        """Generate a diagram."""
        request = DiagramRequest(
            format=format,
            content=content,
            output_format=output_format,
            options=options or {}
        )

        response = await self.client.post(
            f"{self.base_url}/api/v1/diagrams/generate",
            json=request.dict()
        )
        response.raise_for_status()

        return DiagramResult(**response.json())

    async def get_diagram(self, diagram_id: str, filename: str) -> bytes:
        """Retrieve a generated diagram."""
        response = await self.client.get(
            f"{self.base_url}/api/v1/diagrams/{diagram_id}/{filename}"
        )
        response.raise_for_status()
        return response.content
```

## Benefits

1. **Standardization**: Single interface for all diagram generation
2. **Performance**: Centralized caching reduces redundant generation
3. **Scalability**: Service can be scaled independently
4. **Flexibility**: Easy to add new diagram formats
5. **Observability**: Centralized metrics and tracing
6. **Agent Integration**: Agents can programmatically generate diagrams
7. **Documentation Quality**: Consistent, high-quality diagrams across all docs

## Migration Strategy

1. **Phase 1**: Deploy diagram-generator service alongside existing PlantUML service
2. **Phase 2**: Migrate leadership-pitch scripts to use new service
3. **Phase 3**: Integrate with ADR authoring workflow
4. **Phase 4**: Add agent integrations
5. **Phase 5**: Deprecate ad-hoc scripts, consolidate to service

## Testing Strategy

1. **Unit Tests**: Each generator module (mermaid, plantuml, etc.)
2. **Integration Tests**: Service API endpoints
3. **Performance Tests**: Caching effectiveness, generation speed
4. **Regression Tests**: Ensure generated diagrams match expected output
5. **Agent Tests**: Mock integrations with agents

## Metrics and Monitoring

Track:
- Diagrams generated per day/week
- Cache hit rate
- Generation time per diagram format
- Error rate by diagram format
- Most used diagram types
- Service availability

## Future Enhancements

1. **Interactive Diagrams**: Support for D3.js, Vega, Plotly
2. **AI-Generated Diagrams**: LLM integration to generate diagram syntax from text descriptions
3. **Collaborative Editing**: Real-time diagram editing interface
4. **Version Control**: Track diagram changes over time
5. **Template Library**: Pre-built diagram templates for common patterns
6. **Diagram Validation**: Syntax checking and linting
7. **Export Formats**: Additional formats (EPS, EMF, PPTX)

## Related Work

- **PlantUML Service**: Existing diagram generation for UML
- **Leadership Brief**: Proof-of-concept for mermaid integration
- **MLflow**: Artifact tracking for diagrams
- **Documentation Pipeline**: Pandoc/LaTeX integration

## Conclusion

Generalizing diagram generation into mars-core will:
- Eliminate code duplication
- Provide consistent API for all MARS components
- Enable programmatic diagram generation from agents
- Improve documentation quality and maintainability
- Support future AI-powered diagram generation

**Recommended Approach**: Option 3 (Hybrid) - Build the service first, then create the Python client library for seamless integration.
