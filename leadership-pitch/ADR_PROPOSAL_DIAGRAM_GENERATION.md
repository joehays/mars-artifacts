# ADR Proposal: Unified Diagram Generation Service

## Context for ADR Creation

This document outlines the proposal for creating a Strategic ADR in the main MARS repository documenting the decision to create a unified diagram generation service.

**Proposed Location**: `docs/wiki/adr/ADR-XXX-unified-diagram-generation-service.md`

## ADR Outline

### Title
ADR-XXX: Unified Diagram Generation Service for MARS

### Status
Proposed

### Context
MARS currently has fragmented diagram generation capabilities:
1. PlantUML service (containerized at port 8080)
2. Mermaid CLI tools (Node.js, used manually)
3. Ad-hoc conversion scripts (Python, in leadership-pitch)
4. No programmatic API for agents to generate diagrams
5. No centralized caching or standardization

**Pain Points**:
- Agents cannot programmatically generate diagrams
- Duplicate diagram generation logic across projects
- No caching leads to redundant work
- Documentation quality varies due to tool fragmentation
- Hard to maintain and extend diagram capabilities

**Driving Factors**:
1. **Agent Communication**: Need to visualize LangGraph workflows, A2A protocol flows
2. **Provenance Tracking**: Need to generate provenance graphs from Neo4j
3. **Documentation**: ADRs, implementation plans need consistent diagrams
4. **Research Collaboration**: Researchers need to generate diagrams programmatically
5. **Leadership Brief Success**: Mermaid integration proved valuable but needs generalization

### Decision
We will create a unified `diagram-generator` service that:
1. Provides a FastAPI REST API for diagram generation
2. Supports multiple formats: mermaid, plantuml, graphviz, ASCII art
3. Includes Redis-based caching (content hash → generated image)
4. Offers both service (HTTP API) and library (Python client) interfaces
5. Integrates with existing PlantUML service
6. Provides observability (metrics, health checks, tracing)

**Architecture**:
- **Service**: `modules/services/diagram-generator/` (FastAPI, Node.js, Python)
- **Client**: `core/src/mars_framework/diagrams/` (Python library)
- **Caching**: Redis for diagram cache
- **Integration**: Delegates to PlantUML service for UML diagrams

### Consequences

**Positive**:
- ✅ Single interface for all diagram generation
- ✅ Agents can programmatically create diagrams
- ✅ Centralized caching improves performance
- ✅ Easier to add new diagram formats
- ✅ Better observability and metrics
- ✅ Consistent diagram quality across docs
- ✅ Enables future AI-powered diagram generation

**Negative**:
- ⚠️ Additional service to maintain
- ⚠️ Requires Redis dependency
- ⚠️ Migration effort for existing tools
- ⚠️ Node.js dependency for mermaid-cli

**Risks**:
- **Risk 1**: Service becomes single point of failure
  - **Mitigation**: Health checks, auto-restart, fallback to local generation
- **Risk 2**: Cache invalidation complexity
  - **Mitigation**: Content-based hashing (SHA-256) eliminates invalidation
- **Risk 3**: Resource usage for large diagrams
  - **Mitigation**: Rate limiting, timeouts, resource constraints

**Neutral**:
- Replaces ad-hoc scripts with standardized service
- Requires learning new API for diagram generation
- Need to document migration path

### Alternatives Considered

#### Alternative 1: Pure Library Approach
**Description**: Create only a Python library, no service.

**Pros**:
- Simpler architecture
- No HTTP overhead
- Easier to use locally

**Cons**:
- No centralized caching
- Requires tools installed on every machine
- Can't scale independently
- No shared cache across agents

**Decision**: Rejected - Need centralized caching and agent integration.

#### Alternative 2: Extend PlantUML Service
**Description**: Add mermaid support to existing PlantUML service.

**Pros**:
- Reuse existing infrastructure
- One service instead of two

**Cons**:
- PlantUML and Mermaid have different tech stacks
- Hard to maintain mixed codebase
- PlantUML service is UML-focused

**Decision**: Rejected - Better to have specialized services.

#### Alternative 3: Agent-Embedded Generation
**Description**: Each agent implements its own diagram generation.

**Pros**:
- No central service needed
- Agents fully independent

**Cons**:
- Massive code duplication
- No caching
- Inconsistent quality
- Hard to maintain

**Decision**: Rejected - Violates DRY principle.

### Implementation Plan

See `DIAGRAM_GENERATION_GENERALIZATION.md` for detailed plan.

**Summary**:
- Phase 1: Core service (Week 1-2)
- Phase 2: Python client (Week 2-3)
- Phase 3: Advanced generators (Week 3-4)
- Phase 4: Documentation integration (Week 4-5)
- Phase 5: Agent integration (Week 5-6)

**Total Effort**: 6 weeks, 1 FTE

### Related Decisions

- **core/ADR-0009 (Module Directory Schema)**: Diagram service follows standard module structure
- **docs/wiki/ADR-015 (MARS-DEV Module)**: mars-dev uses diagrams for documentation
- **PlantUML Service**: Existing diagram capability, will be integrated
- **Leadership Brief**: Proof-of-concept for mermaid integration

### References

- Design Document: `DIAGRAM_GENERATION_GENERALIZATION.md`
- PlantUML Service: `modules/services/plantuml/`
- Leadership Brief: `external/mars-artifacts/leadership-pitch/`
- Mermaid.js: https://mermaid.js.org/
- PlantUML: https://plantuml.com/
- GraphViz: https://graphviz.org/

### Notes

**Testing Strategy**:
- Unit tests for each generator
- Integration tests for service API
- Performance tests for caching
- Agent integration tests

**Security Considerations**:
- Input validation for diagram syntax
- Sandboxing for code execution
- Rate limiting to prevent abuse
- Resource limits (memory, CPU, time)

**Compliance**:
- Follows P2 Security by Design (isolation, least privilege)
- Follows P8 Provenance (track diagram generation in Neo4j)
- Follows module directory schema (ADR-0009)

## Action Items

1. **Create ADR in main repository**:
   ```bash
   cd /workspace/mars-v2
   # Find next ADR number
   ls docs/wiki/adr/ | grep -E "^ADR-[0-9]+" | sort -V | tail -1
   # Create new ADR file
   cp docs/wiki/templates/ADR_TEMPLATE.md docs/wiki/adr/ADR-XXX-unified-diagram-generation-service.md
   # Fill in content from this proposal
   ```

2. **Copy design document to main repository**:
   ```bash
   cp external/mars-artifacts/leadership-pitch/DIAGRAM_GENERATION_GENERALIZATION.md \
      docs/wiki/implementation-plans/diagram-generation-service.md
   ```

3. **Prototype diagram-generator service**:
   ```bash
   mkdir -p modules/services/diagram-generator
   cd modules/services/diagram-generator
   # Create initial structure
   ```

4. **Update roadmap**:
   - Add diagram-generator to Component inventory
   - Schedule implementation (Q1 2026?)
   - Identify dependencies and prerequisites

## Summary

This ADR proposal documents the decision to create a unified diagram generation service for MARS. The service will:
- Consolidate fragmented diagram capabilities
- Enable programmatic diagram generation from agents
- Improve documentation quality and consistency
- Support future AI-powered diagram generation

**Next Steps**: Create formal ADR in main repository, prototype service, integrate with existing tools.
