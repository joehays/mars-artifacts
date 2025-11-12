#!/usr/bin/env python3
"""
Convert mermaid code blocks to PDF image references in markdown.

This script replaces embedded mermaid diagrams with references to
pre-generated PDF files in the diagrams/ directory.

Usage:
    python3 convert_mermaid_to_images.py LEADERSHIP_BRIEF_ORCHESTRATED_AI.md > LEADERSHIP_BRIEF_WITH_IMAGES.md
"""

import sys
import re

# Mapping of mermaid diagrams to their PDF filenames
# Based on the diagram content, we can identify which diagram it is
DIAGRAM_MAPPING = {
    'A2A Protocol': 'diagrams/a2a-protocol.pdf',
    'ADR Authoring': 'diagrams/adr-authoring-workflow.pdf',
    'GitLab CI Pipeline': 'diagrams/gitlab-ci-pipeline.pdf',
    'LangGraph State Machine': 'diagrams/langgraph-state-machine.pdf',
    'MCP Protocol': 'diagrams/mcp-protocol.pdf',
    'Merge Request': 'diagrams/merge-request-workflow.pdf',
    'OpenTelemetry': 'diagrams/opentelemetry-trace.pdf',
    'Pre-Commit Hook': 'diagrams/precommit-hook-flow.pdf',
    'Pre-commit Hook': 'diagrams/precommit-hook-flow.pdf',
}

def identify_diagram(content_text):
    """Identify which diagram based on content keywords and context."""
    content_lower = content_text.lower()

    # Check for architecture diagrams (ASCII art in plain code blocks)
    if 'mars runtime architecture' in content_lower or 'mars-rt architecture' in content_lower:
        return 'diagrams/mars-rt-architecture.pdf'
    elif 'mars-dev infrastructure' in content_lower or 'development tools & processes' in content_lower:
        return 'diagrams/mars-dev-architecture.pdf'
    elif 'design next experiment' in content_lower and 'orchestrator' in content_lower and ('literature agent' in content_lower or 'data agent' in content_lower):
        return 'diagrams/orchestration-flow.pdf'

    # Check for mermaid diagrams
    elif 'pre-commit' in content_lower or 'precommit' in content_lower or 'git commit' in content_lower or 'hook' in content_lower:
        return 'diagrams/precommit-hook-flow.pdf'
    elif 'merge request' in content_lower or 'peer review' in content_lower or 'code review' in content_lower:
        return 'diagrams/merge-request-workflow.pdf'
    elif 'adr' in content_lower and ('draft' in content_lower or 'review' in content_lower or 'architectural' in content_lower):
        return 'diagrams/adr-authoring-workflow.pdf'
    elif 'gitlab ci' in content_lower or ('pipeline' in content_lower and 'stage' in content_lower and 'lint' in content_lower):
        return 'diagrams/gitlab-ci-pipeline.pdf'
    elif 'langgraph' in content_lower or 'state machine' in content_lower or 'supervisor' in content_lower:
        return 'diagrams/langgraph-state-machine.pdf'
    elif 'mcp' in content_lower or 'model context protocol' in content_lower or 'tool provider' in content_lower:
        return 'diagrams/mcp-protocol.pdf'
    elif 'opentelemetry' in content_lower or 'trace-id' in content_lower or 'x-trace-id' in content_lower or 'distributed tracing' in content_lower:
        return 'diagrams/opentelemetry-trace.pdf'
    elif 'a2a' in content_lower or 'agent-to-agent' in content_lower or ('agentfrom' in content_lower and 'agentto' in content_lower):
        return 'diagrams/a2a-protocol.pdf'
    else:
        return None

def convert_plain_code_blocks(content):
    """Replace plain code blocks (ASCII art) with image references."""

    # Pattern to match plain code blocks (no language specifier) that might be diagrams
    # The negative lookahead (?![a-z]) ensures we don't match ```mermaid or other language specifiers
    # Only convert if they contain box-drawing characters or are architecture diagrams
    pattern = r'(.{0,500})```(?![a-z])\n(.*?)```'

    diagram_count = 0
    identified_count = 0

    def replacer(match):
        nonlocal diagram_count, identified_count
        context_before = match.group(1)
        code_content = match.group(2)

        # Only try to convert if it looks like an ASCII art diagram
        # Check for box-drawing characters
        has_box_chars = ('┌' in code_content or '│' in code_content or '└' in code_content)

        # Check if it's in a known architecture section
        has_arch_header = ('### The Complete MARS-RT Architecture' in context_before or
                          '### The Complete mars-dev Architecture' in context_before)

        # Check for orchestration flow diagram (section 3.5)
        is_orch_flow = ('Task: Design Next Experiment' in code_content and
                       'Orchestrator' in code_content and has_box_chars)

        # For large diagrams, require both box chars and size
        is_large_diagram = has_box_chars and len(code_content) > 500

        if is_large_diagram or has_arch_header or is_orch_flow:
            diagram_count += 1
            # Combine context and content for identification
            combined_text = context_before + "\n" + code_content
            diagram_path = identify_diagram(combined_text)

            if diagram_path:
                identified_count += 1
                # Return markdown image reference (preserve context before)
                # Center-aligned with width constraint
                return f'{context_before}\n\n![Architecture Diagram {diagram_count}]({diagram_path}){{ width=100% }}\n'
            else:
                # Keep original if we can't identify
                print(f"Warning: Could not identify ASCII diagram {diagram_count}", file=sys.stderr)
                headers = re.findall(r'(###? .*)', context_before)
                if headers:
                    print(f"  Header: {headers[-1]}", file=sys.stderr)
                return match.group(0)
        else:
            # Not a diagram, keep original
            return match.group(0)

    result = re.sub(pattern, replacer, content, flags=re.DOTALL)

    if diagram_count > 0:
        print(f"Found {diagram_count} plain code block diagrams", file=sys.stderr)
        print(f"Identified {identified_count} ASCII diagrams", file=sys.stderr)
        if diagram_count > identified_count:
            print(f"Warning: {diagram_count - identified_count} ASCII diagrams could not be identified", file=sys.stderr)

    return result

def convert_mermaid_blocks(content):
    """Replace mermaid code blocks with image references."""

    # Pattern to match mermaid code blocks with context before
    # Captures up to 500 chars before the mermaid block to get the header
    pattern = r'(.{0,500})```mermaid\n(.*?)```'

    diagram_count = 0
    identified_count = 0

    def replacer(match):
        nonlocal diagram_count, identified_count
        diagram_count += 1
        context_before = match.group(1)
        mermaid_content = match.group(2)

        # Combine context and content for identification
        combined_text = context_before + "\n" + mermaid_content
        diagram_path = identify_diagram(combined_text)

        if diagram_path:
            identified_count += 1
            # Return markdown image reference (preserve context before)
            # Using width=100% to fill available space (LaTeX will scale via header.tex)
            # Centered with extra newlines for proper spacing
            return f'{context_before}\n\n![Diagram {diagram_count}]({diagram_path}){{ width=100% }}\n'
        else:
            # Keep original if we can't identify
            print(f"Warning: Could not identify mermaid diagram {diagram_count}", file=sys.stderr)
            # Extract last header from context
            headers = re.findall(r'(###? .*)', context_before)
            if headers:
                print(f"  Header: {headers[-1]}", file=sys.stderr)
            print(f"  Content preview: {mermaid_content[:100]}...", file=sys.stderr)
            return match.group(0)

    result = re.sub(pattern, replacer, content, flags=re.DOTALL)

    print(f"Found {diagram_count} mermaid diagrams", file=sys.stderr)
    print(f"Identified {identified_count} mermaid diagrams", file=sys.stderr)
    if diagram_count > identified_count:
        print(f"Warning: {diagram_count - identified_count} mermaid diagrams could not be identified", file=sys.stderr)

    return result

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 convert_mermaid_to_images.py INPUT.md > OUTPUT.md", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    # Convert plain code blocks FIRST (before mermaid conversion)
    # This ensures ASCII art diagrams are detected correctly before mermaid blocks are removed
    print("Converting ASCII art diagrams...", file=sys.stderr)
    content = convert_plain_code_blocks(content)

    print("\nConverting mermaid diagrams...", file=sys.stderr)
    content = convert_mermaid_blocks(content)

    print("\nConversion complete!", file=sys.stderr)

    print(content)

if __name__ == '__main__':
    main()
