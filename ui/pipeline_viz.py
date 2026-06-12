"""
ui/pipeline_viz.py — Pipeline State Machine Visualization
==========================================================
Renders an SVG pipeline diagram showing all 7 agents as nodes
with connecting arrows. The active agent is highlighted in orange.
"""

from __future__ import annotations

from typing import List, Optional

import streamlit as st

from pipeline.state import AgentStatus, AgentTrace


AGENT_LABELS = [
    ("1", "Voice\nIntake"),
    ("2", "Skill\nExtract"),
    ("3", "Resume\nBuilder"),
    ("4", "Job\nMatcher"),
    ("5", "Interview\nCoach"),
    ("6", "Apply\nAgent"),
    ("7", "Status\nTracker"),
]

STATUS_COLORS = {
    AgentStatus.WAITING:  ("#334155", "#64748B"),   # (fill, stroke)
    AgentStatus.RUNNING:  ("#7C2D12", "#F97316"),
    AgentStatus.DONE:     ("#064E3B", "#10B981"),
    AgentStatus.ERROR:    ("#7F1D1D", "#EF4444"),
    AgentStatus.SKIPPED:  ("#1E293B", "#475569"),
}


def render_pipeline_viz(
    traces: List[AgentTrace],
    current_agent: int = 0,
    total_elapsed_ms: Optional[int] = None,
) -> None:
    """Render the SVG pipeline diagram."""

    W = 960   # SVG width
    H = 120   # SVG height
    NODE_W = 80
    NODE_H = 54
    NODE_Y = (H - NODE_H) // 2
    ARROW_Y = H // 2

    # Spacing
    total_nodes = len(AGENT_LABELS)
    spacing = (W - total_nodes * NODE_W) / (total_nodes + 1)

    nodes_svg = []
    arrows_svg = []

    for i, (num, label) in enumerate(AGENT_LABELS):
        x = spacing * (i + 1) + NODE_W * i
        cx = x + NODE_W / 2

        trace = traces[i] if i < len(traces) else None
        status = trace.status if trace else AgentStatus.WAITING
        fill, stroke = STATUS_COLORS[status]

        is_active = trace and trace.status == AgentStatus.RUNNING
        glow = f'filter="url(#glow)"' if is_active else ""

        # Arrow to next node
        if i < total_nodes - 1:
            next_x = spacing * (i + 2) + NODE_W * (i + 1)
            arrow_x1 = x + NODE_W + 2
            arrow_x2 = next_x - 2
            arrow_color = "#F97316" if (trace and trace.status == AgentStatus.DONE) else "#334155"
            arrows_svg.append(f"""
                <line x1="{arrow_x1}" y1="{ARROW_Y}" x2="{arrow_x2}" y2="{ARROW_Y}"
                      stroke="{arrow_color}" stroke-width="2"
                      marker-end="url(#arrowhead_{arrow_color.replace('#','')})"/>
            """)

        # Timing label
        timing_label = ""
        if trace and trace.elapsed_ms is not None:
            timing_label = f"""
                <text x="{cx}" y="{NODE_Y + NODE_H + 14}"
                      text-anchor="middle" font-size="9" fill="#94A3B8">
                    {trace.elapsed_ms}ms
                </text>
            """

        # Status icon
        icons = {
            AgentStatus.WAITING:  "⏳",
            AgentStatus.RUNNING:  "⚡",
            AgentStatus.DONE:     "✓",
            AgentStatus.ERROR:    "✗",
            AgentStatus.SKIPPED:  "–",
        }
        icon = icons.get(status, "⏳")

        # Wrap label
        label_lines = label.split("\n")
        label_svg = ""
        for j, line in enumerate(label_lines):
            label_svg += f"""
                <text x="{cx}" y="{NODE_Y + 28 + j * 13}"
                      text-anchor="middle" font-size="9" fill="#E2E8F0"
                      font-weight="600">{line}</text>
            """

        nodes_svg.append(f"""
            <g>
                <rect x="{x}" y="{NODE_Y}" width="{NODE_W}" height="{NODE_H}"
                      rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"
                      {glow}/>
                <text x="{cx}" y="{NODE_Y + 14}"
                      text-anchor="middle" font-size="10" fill="{stroke}"
                      font-weight="700">A{num}</text>
                {label_svg}
                {timing_label}
            </g>
        """)

    # Total time badge
    elapsed_badge = ""
    if total_elapsed_ms is not None:
        elapsed_badge = f"""
            <text x="{W - 10}" y="16" text-anchor="end"
                  font-size="11" fill="#F97316" font-weight="700">
                Total: {total_elapsed_ms / 1000:.1f}s
            </text>
        """

    svg = f"""
    <svg width="100%" viewBox="0 0 {W} {H + 20}"
         xmlns="http://www.w3.org/2000/svg"
         style="background:#0D1B2E; border-radius:12px; padding:8px;">
        <defs>
            <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <marker id="arrowhead_F97316" markerWidth="8" markerHeight="6"
                    refX="7" refY="3" orient="auto">
                <polygon points="0 0, 8 3, 0 6" fill="#F97316"/>
            </marker>
            <marker id="arrowhead_334155" markerWidth="8" markerHeight="6"
                    refX="7" refY="3" orient="auto">
                <polygon points="0 0, 8 3, 0 6" fill="#334155"/>
            </marker>
        </defs>
        {''.join(arrows_svg)}
        {''.join(nodes_svg)}
        {elapsed_badge}
    </svg>
    """

    st.markdown(svg, unsafe_allow_html=True)


def render_pipeline_status_bar(
    traces: List[AgentTrace],
    current_agent: int,
    total_elapsed_ms: Optional[int] = None,
) -> None:
    """Render a compact status bar showing pipeline progress."""

    done_count = sum(1 for t in traces if t.status == AgentStatus.DONE)
    error_count = sum(1 for t in traces if t.status == AgentStatus.ERROR)
    total = len(traces)

    pct = (done_count / total) * 100

    bar_color = "#EF4444" if error_count else "#F97316" if done_count < total else "#10B981"

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"""
            <div style="background:#1A2E4A; border-radius:8px; overflow:hidden; height:8px; margin-top:8px;">
                <div style="background:{bar_color}; width:{pct:.0f}%; height:100%;
                            transition:width 0.5s ease; border-radius:8px;"></div>
            </div>
            <div style="font-size:10px; color:#94A3B8; margin-top:4px;">
                {done_count}/{total} agents complete
                {f"• ❌ {error_count} error(s)" if error_count else ""}
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if total_elapsed_ms:
            st.metric("⏱ Total", f"{total_elapsed_ms / 1000:.1f}s")
    with col3:
        if current_agent > 0:
            st.metric("🔄 Active", f"Agent {current_agent}")
