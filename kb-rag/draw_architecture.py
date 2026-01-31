"""
Draw LangGraph Architecture Diagram using Matplotlib
Creates a custom visual diagram of the RAG chatbot workflow
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def draw_architecture_diagram():
    """Create a professional architecture diagram"""

    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Title
    ax.text(5, 11.5, 'LangGraph RAG Chatbot Architecture',
            fontsize=20, fontweight='bold', ha='center')

    # Color scheme
    color_input = '#E3F2FD'      # Light blue
    color_agent1 = '#BBDEFB'     # Blue
    color_agent2 = '#FFF3E0'     # Orange
    color_decision = '#F3E5F5'   # Purple
    color_agent3 = '#E8F5E9'     # Green
    color_fallback = '#FFEBEE'   # Red
    color_output = '#F5F5F5'     # Gray

    # Helper function to draw boxes
    def draw_box(x, y, width, height, text, color, fontsize=10):
        box = FancyBboxPatch(
            (x - width/2, y - height/2), width, height,
            boxstyle="round,pad=0.1",
            edgecolor='black',
            facecolor=color,
            linewidth=2
        )
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=fontsize, ha='center', va='center',
                fontweight='bold', wrap=True)

    # Helper function to draw arrows
    def draw_arrow(x1, y1, x2, y2, label='', curved=False):
        if curved:
            style = "arc3,rad=.3"
        else:
            style = "arc3,rad=0"

        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle='->',
            mutation_scale=20,
            linewidth=2,
            color='black',
            connectionstyle=style
        )
        ax.add_patch(arrow)

        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mid_x + 0.3, mid_y, label, fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black'))

    # 1. User Input
    draw_box(5, 10, 3, 0.6, 'User Question\n"What causes OOM errors?"', color_input, 11)

    # Arrow to Agent 1
    draw_arrow(5, 9.7, 5, 9.2)

    # 2. Agent 1: Query Processor
    draw_box(5, 8.5, 3.5, 1.2,
             'AGENT 1: Query Processor\n\n'
             '• Clean & normalize query\n'
             '• Generate embedding (1536D)\n'
             '• OpenAI API',
             color_agent1, 9)

    # Arrow to Agent 2
    draw_arrow(5, 7.9, 5, 7.2)

    # 3. Agent 2: RAG Retriever
    draw_box(5, 6.3, 3.5, 1.4,
             'AGENT 2: RAG Retriever\n\n'
             '• Search Weaviate vector DB\n'
             '• TOP_K_CHUNKS = 3\n'
             '• DISTANCE_THRESHOLD = 0.7\n'
             '• Filter by relevance',
             color_agent2, 9)

    # Arrow to Decision
    draw_arrow(5, 5.6, 5, 4.9)

    # 4. Decision Node
    draw_box(5, 4.3, 2.5, 0.8,
             'Chunks Found?\ntotal_relevant > 0',
             color_decision, 10)

    # Arrow to Agent 3 (YES)
    draw_arrow(5, 3.9, 2.5, 3.2, 'YES', curved=True)

    # Arrow to Fallback (NO)
    draw_arrow(5, 3.9, 7.5, 3.2, 'NO', curved=True)

    # 5A. Agent 3: Answer Generator
    draw_box(2.5, 2.3, 3.5, 1.4,
             'AGENT 3: Answer Generator\n\n'
             '• Build context from chunks\n'
             '• LLM: gpt-4o-mini\n'
             '• TEMPERATURE = 0.3\n'
             '• Generate answer + sources',
             color_agent3, 9)

    # 5B. Fallback Node
    draw_box(7.5, 2.3, 3.5, 1.4,
             'FALLBACK NODE\n\n'
             '• No relevant chunks\n'
             '• Generic response\n'
             '• "I couldn\'t find..."\n'
             '• Confidence: 20%',
             color_fallback, 9)

    # Arrows to END
    draw_arrow(2.5, 1.6, 3.5, 0.9, curved=True)
    draw_arrow(7.5, 1.6, 6.5, 0.9, curved=True)

    # 6. Final Response
    draw_box(5, 0.5, 4, 0.6,
             'Final Response to User\n'
             'Answer + Sources + Metadata + Confidence',
             color_output, 10)

    # Configuration Box (top right)
    config_text = (
        'Configuration\n'
        '(config.py)\n\n'
        'TOP_K_CHUNKS = 3\n'
        'DISTANCE_THRESHOLD = 0.7\n'
        'TEMPERATURE = 0.3\n'
        'LLM_MODEL = gpt-4o-mini'
    )
    draw_box(8.5, 9.5, 2.5, 1.8, config_text, '#FFF9C4', 8)

    # State Flow Box (top left)
    state_text = (
        'State Variables\n\n'
        '• user_question\n'
        '• query_embedding\n'
        '• retrieved_chunks\n'
        '• final_answer\n'
        '• sources\n'
        '• confidence_score'
    )
    draw_box(1.5, 9.5, 2.5, 1.8, state_text, '#E1F5FE', 8)

    # Legend
    legend_elements = [
        mpatches.Patch(color=color_agent1, label='Agent 1: Query Processing'),
        mpatches.Patch(color=color_agent2, label='Agent 2: RAG Retrieval'),
        mpatches.Patch(color=color_agent3, label='Agent 3: Answer Generation'),
        mpatches.Patch(color=color_fallback, label='Fallback Response'),
        mpatches.Patch(color=color_decision, label='Decision Node'),
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=8)

    # Footer
    ax.text(5, -0.2,
            'AI DevOps Platform - RAG Chatbot | LangGraph Multi-Agent System',
            fontsize=9, ha='center', style='italic', color='gray')

    # Save figure
    plt.tight_layout()

    output_file = 'langgraph_architecture.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Architecture diagram saved to: {output_file}")

    # Also save as PDF
    output_pdf = 'langgraph_architecture.pdf'
    plt.savefig(output_pdf, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ PDF diagram saved to: {output_pdf}")

    plt.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  LANGGRAPH ARCHITECTURE DIAGRAM GENERATOR")
    print("="*60 + "\n")

    try:
        draw_architecture_diagram()
        print("\n✅ Diagram generation complete!")
        print("\nGenerated files:")
        print("  - langgraph_architecture.png (High-resolution image)")
        print("  - langgraph_architecture.pdf (Vector PDF)")

    except ImportError as e:
        print(f"❌ Missing dependency: {str(e)}")
        print("\nInstall matplotlib:")
        print("  pip install matplotlib")
    except Exception as e:
        print(f"❌ Error generating diagram: {str(e)}")
