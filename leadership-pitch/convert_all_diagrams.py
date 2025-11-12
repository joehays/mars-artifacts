#!/usr/bin/env python3
"""
Convert all diagrams (mermaid, ASCII architecture, orchestration flow) to image references.

This script uses line-based replacement for the large ASCII architecture diagrams
to avoid regex matching issues, then uses regex for mermaid diagrams and the
orchestration flow diagram.
"""

import sys
import re

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 convert_all_diagrams.py INPUT.md > OUTPUT.md", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    print(f"Total lines in input: {len(lines)}", file=sys.stderr)

    # Step 1: Replace MARS-RT architecture diagram (lines 5187-5542)
    # Line 5187: ### The Complete MARS-RT Architecture
    # Line 5188: (blank)
    # Line 5189: ```
    # Lines 5190-5541: ASCII art
    # Line 5542: ```
    print("\nReplacing MARS-RT architecture diagram (lines 5187-5542)...", file=sys.stderr)
    replacement_mars_rt = [
        "### The Complete MARS-RT Architecture\n",
        "\n",
        "![MARS Runtime Architecture](diagrams/mars-rt-architecture.pdf){ width=100% }\n",
        "\n"
    ]

    # Replace lines 5186-5541 (0-indexed: 5186-5541)
    lines[5186:5542] = replacement_mars_rt
    print(f"  Replaced {5542-5186} lines with {len(replacement_mars_rt)} lines", file=sys.stderr)
    print(f"  New total lines: {len(lines)}", file=sys.stderr)

    # Step 2: Replace mars-dev architecture diagram
    # After step 1, line numbers have shifted
    # Original lines 5584-5910 → Now approximately lines 5584 - (5542-5186) + len(replacement_mars_rt)
    # Shift = -(5542-5186) + len(replacement_mars_rt) = -356 + 4 = -352
    # New line for "### The Complete mars-dev Architecture" = 5584 - 352 = 5232

    # Let's find it dynamically
    mars_dev_header_line = None
    for i, line in enumerate(lines):
        if '### The Complete mars-dev Architecture' in line:
            mars_dev_header_line = i
            break

    if mars_dev_header_line is not None:
        print(f"\nFound mars-dev architecture header at line {mars_dev_header_line + 1}", file=sys.stderr)

        # Find the closing backticks
        start_backtick = None
        end_backtick = None

        # Start searching from header line
        for i in range(mars_dev_header_line, min(len(lines), mars_dev_header_line + 500)):
            if '```' in lines[i] and start_backtick is None:
                start_backtick = i
            elif '```' in lines[i] and start_backtick is not None and i > start_backtick:
                end_backtick = i
                break

        if start_backtick and end_backtick:
            print(f"  Diagram from line {start_backtick + 1} to {end_backtick + 1}", file=sys.stderr)

            replacement_mars_dev = [
                "### The Complete mars-dev Architecture\n",
                "\n",
                "![mars-dev Architecture](diagrams/mars-dev-architecture.pdf){ width=100% }\n",
                "\n"
            ]

            # Replace from header to end of diagram
            lines[mars_dev_header_line:end_backtick+1] = replacement_mars_dev
            print(f"  Replaced {end_backtick - mars_dev_header_line + 1} lines with {len(replacement_mars_dev)} lines", file=sys.stderr)
            print(f"  New total lines: {len(lines)}", file=sys.stderr)
    else:
        print("  ⚠️ mars-dev architecture header not found", file=sys.stderr)

    # Step 3: Convert to string and process mermaid diagrams
    content = ''.join(lines)

    print("\nConverting mermaid diagrams...", file=sys.stderr)
    mermaid_pattern = r'(.{0,500})```mermaid\n(.*?)```'
    mermaid_count = 0

    def mermaid_replacer(match):
        nonlocal mermaid_count
        mermaid_count += 1
        context_before = match.group(1)
        mermaid_content = match.group(2)

        # Identify diagram type by looking at the header in context (more reliable)
        context_lower = context_before.lower()

        # Match based on section headers (most reliable)
        if 'how mcp protocol works' in context_lower:
            diagram_path = 'diagrams/mcp-protocol.pdf'
        elif 'how a2a protocol works' in context_lower:
            diagram_path = 'diagrams/a2a-protocol.pdf'
        elif 'how langgraph protocol works' in context_lower:
            diagram_path = 'diagrams/langgraph-state-machine.pdf'
        elif 'how opentelemetry protocol works' in context_lower:
            diagram_path = 'diagrams/opentelemetry-trace.pdf'
        elif 'protocol 1: pre-commit' in context_lower or 'pre-commit hooks' in context_lower:
            diagram_path = 'diagrams/precommit-hook-flow.pdf'
        elif 'protocol 2: gitlab ci' in context_lower or 'ci/cd pipeline' in context_lower:
            diagram_path = 'diagrams/gitlab-ci-pipeline.pdf'
        elif 'protocol 3: merge request' in context_lower:
            diagram_path = 'diagrams/merge-request-workflow.pdf'
        elif 'protocol 4: adr' in context_lower or 'adr authoring' in context_lower:
            diagram_path = 'diagrams/adr-authoring-workflow.pdf'
        else:
            # Keep original if we can't identify
            print(f"  Warning: Could not identify mermaid diagram {mermaid_count}", file=sys.stderr)
            print(f"    Context: {context_before[-100:]}", file=sys.stderr)
            return match.group(0)

        return f'{context_before}\n\n![Diagram]({diagram_path}){{ width=100% }}\n'

    content = re.sub(mermaid_pattern, mermaid_replacer, content, flags=re.DOTALL)
    print(f"  Converted {mermaid_count} mermaid diagrams", file=sys.stderr)

    # Step 4: Convert orchestration flow diagram (plain code block with box chars)
    print("\nConverting orchestration flow diagram...", file=sys.stderr)
    orch_pattern = r'(.{0,500})```\n(Task: Design Next Experiment.*?)```'
    orch_count = 0

    def orch_replacer(match):
        nonlocal orch_count
        context_before = match.group(1)
        code_content = match.group(2)

        # Check if it's the orchestration flow
        if 'Task: Design Next Experiment' in code_content and 'Orchestrator' in code_content:
            orch_count += 1
            return f'{context_before}\n\n![Orchestration Flow](diagrams/orchestration-flow.pdf){{ width=100% }}\n'
        else:
            return match.group(0)

    content = re.sub(orch_pattern, orch_replacer, content, flags=re.DOTALL)
    print(f"  Converted {orch_count} orchestration flow diagrams", file=sys.stderr)

    print("\nConversion complete!", file=sys.stderr)
    print(f"Total diagrams converted: {2 + mermaid_count + orch_count}", file=sys.stderr)
    print("  - 2 architecture diagrams (line-based replacement)", file=sys.stderr)
    print(f"  - {mermaid_count} mermaid diagrams", file=sys.stderr)
    print(f"  - {orch_count} orchestration flow diagrams", file=sys.stderr)

    print(content)

if __name__ == '__main__':
    main()
