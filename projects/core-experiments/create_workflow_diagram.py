#!/usr/bin/env python3
"""Workflow Diagram Generator
=========================

Creates a visual diagram showing the quantum reproducibility workflow layers:
Baseline → Discrepancy → CanonicalFix → Scaling → Noise → Cloud

This helps newcomers understand the narrative structure instantly.
"""

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def create_workflow_diagram():
    """Create the workflow diagram showing all layers"""
    # Set up the figure
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # Define colors for each layer
    colors = {
        "baseline": "#E8F4FD",  # Light blue
        "discrepancy": "#FFE6E6",  # Light red
        "canonical": "#E6F7E6",  # Light green
        "scaling": "#FFF2E6",  # Light orange
        "noise": "#F0E6FF",  # Light purple
        "cloud": "#E6F0FF",  # Light blue-gray
    }

    # Define the workflow layers
    layers = [
        {
            "name": "Baseline",
            "title": "1. Baseline Implementation",
            "description": "Original MaxCut calculation\nwith lookup table approach",
            "position": (1, 10),
            "color": colors["baseline"],
            "outputs": ["Bell state fidelity: 1.000", "QAOA expectation: 0.562"],
        },
        {
            "name": "Discrepancy",
            "title": "2. Discrepancy Discovery",
            "description": "Independent verification reveals\n25% agreement rate",
            "position": (3, 10),
            "color": colors["discrepancy"],
            "outputs": ["Verification fails", "Root cause unknown"],
        },
        {
            "name": "Canonical",
            "title": "3. Canonical Fix",
            "description": "Align with PennyLane standard\nDirect edge counting",
            "position": (5, 10),
            "color": colors["canonical"],
            "outputs": ["100% PennyLane match", "Validated implementation"],
        },
        {
            "name": "Scaling",
            "title": "4. Scaling Analysis",
            "description": "Test performance across\ndifferent problem sizes",
            "position": (7, 10),
            "color": colors["scaling"],
            "outputs": ["Exponential scaling", "Memory limitations"],
        },
        {
            "name": "Noise",
            "title": "5. Noise Modeling",
            "description": "Add depolarizing noise\nto simulate real hardware",
            "position": (1, 6),
            "color": colors["noise"],
            "outputs": ["Realistic fidelities", "Error characterization"],
        },
        {
            "name": "Cloud",
            "title": "6. Cloud Validation",
            "description": "Deploy to AWS Braket\nReal quantum hardware",
            "position": (3, 6),
            "color": colors["cloud"],
            "outputs": ["Hardware validation", "Cost analysis"],
        },
    ]

    # Draw the layers
    boxes = {}
    for layer in layers:
        x, y = layer["position"]

        # Main box
        box = FancyBboxPatch(
            (x - 0.8, y - 1.5),
            1.6,
            2.5,
            boxstyle="round,pad=0.1",
            facecolor=layer["color"],
            edgecolor="black",
            linewidth=1.5,
        )
        ax.add_patch(box)
        boxes[layer["name"]] = box

        # Title
        ax.text(
            x,
            y + 0.8,
            layer["title"],
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
        )

        # Description
        ax.text(x, y + 0.1, layer["description"], ha="center", va="center", fontsize=9)

        # Outputs
        for i, output in enumerate(layer["outputs"]):
            ax.text(
                x,
                y - 0.5 - i * 0.3,
                f"• {output}",
                ha="center",
                va="center",
                fontsize=8,
                style="italic",
            )

    # Draw arrows between layers
    arrows = [
        ("Baseline", "Discrepancy"),
        ("Discrepancy", "Canonical"),
        ("Canonical", "Scaling"),
        ("Scaling", "Noise"),
        ("Noise", "Cloud"),
    ]

    for start, end in arrows:
        start_layer = next(l for l in layers if l["name"] == start)
        end_layer = next(l for l in layers if l["name"] == end)

        start_pos = start_layer["position"]
        end_pos = end_layer["position"]

        # Special handling for the wrap-around arrow
        if start == "Scaling" and end == "Noise":
            # Curved arrow going down and left
            ax.annotate(
                "",
                xy=(end_pos[0] + 0.5, end_pos[1] + 1.5),
                xytext=(start_pos[0] - 0.5, start_pos[1] - 1.5),
                arrowprops=dict(
                    arrowstyle="->",
                    lw=2,
                    color="darkblue",
                    connectionstyle="arc3,rad=0.3",
                ),
            )
        else:
            # Straight arrows
            ax.annotate(
                "",
                xy=(end_pos[0] - 0.8, end_pos[1]),
                xytext=(start_pos[0] + 0.8, start_pos[1]),
                arrowprops=dict(arrowstyle="->", lw=2, color="darkblue"),
            )

    # Add title and subtitle
    ax.text(
        5,
        11.5,
        "Quantum Reproducibility Workflow",
        ha="center",
        va="center",
        fontsize=16,
        fontweight="bold",
    )
    ax.text(
        5,
        11,
        "From Implementation Discrepancy to Educational Resource",
        ha="center",
        va="center",
        fontsize=12,
        style="italic",
    )

    # Add legend
    legend_elements = [
        mpatches.Patch(color=colors["baseline"], label="Implementation"),
        mpatches.Patch(color=colors["discrepancy"], label="Problem Discovery"),
        mpatches.Patch(color=colors["canonical"], label="Solution"),
        mpatches.Patch(color=colors["scaling"], label="Analysis"),
        mpatches.Patch(color=colors["noise"], label="Modeling"),
        mpatches.Patch(color=colors["cloud"], label="Validation"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(0.98, 0.98))

    # Add educational outcomes box
    outcomes_box = FancyBboxPatch(
        (5.5, 2),
        4,
        3,
        boxstyle="round,pad=0.2",
        facecolor="#F0F8FF",
        edgecolor="navy",
        linewidth=2,
    )
    ax.add_patch(outcomes_box)

    ax.text(
        7.5,
        4.5,
        "Educational Outcomes",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="navy",
    )

    outcomes = [
        "✓ Reproducibility best practices",
        "✓ Implementation validation methods",
        "✓ Quantum algorithm debugging",
        "✓ Cloud quantum computing",
        "✓ Statistical analysis techniques",
        "✓ Scientific methodology",
    ]

    for i, outcome in enumerate(outcomes):
        ax.text(7.5, 4.1 - i * 0.25, outcome, ha="center", va="center", fontsize=9)

    # Add problem statement
    problem_box = FancyBboxPatch(
        (0.5, 2),
        4,
        3,
        boxstyle="round,pad=0.2",
        facecolor="#FFF8DC",
        edgecolor="darkgoldenrod",
        linewidth=2,
    )
    ax.add_patch(problem_box)

    ax.text(
        2.5,
        4.5,
        "The Great QAOA Mystery",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="darkgoldenrod",
    )

    ax.text(
        2.5,
        4,
        "Why did two implementations of the same\nMaxCut algorithm give different results?",
        ha="center",
        va="center",
        fontsize=10,
        style="italic",
    )

    mystery_points = [
        "• Original: 0.562 expected cut",
        "• Verification: 0.142 expected cut",
        "• Difference: 0.420 (74% error!)",
        "• Quantum circuits identical",
        "• Classical calculation differs",
    ]

    for i, point in enumerate(mystery_points):
        ax.text(2.5, 3.4 - i * 0.2, point, ha="center", va="center", fontsize=8)

    plt.tight_layout()
    return fig


def save_workflow_diagram(filename="workflow_diagram.png", dpi=300):
    """Save the workflow diagram to file"""
    fig = create_workflow_diagram()
    fig.savefig(filename, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"✅ Workflow diagram saved as {filename}")


def main():
    """Generate and display the workflow diagram"""
    print("🎨 Creating workflow diagram...")

    # Create the diagram
    fig = create_workflow_diagram()

    # Save to file
    save_workflow_diagram("docs/workflow_diagram.png")

    # Display
    plt.show()

    print("📊 Workflow diagram created successfully!")
    print("   This helps newcomers understand the narrative structure instantly.")


if __name__ == "__main__":
    main()
