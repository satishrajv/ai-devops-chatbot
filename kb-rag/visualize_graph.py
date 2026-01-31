"""
Visualize the LangGraph RAG Chatbot workflow
Generates PNG and SVG diagrams showing the multi-agent architecture
"""

import os
from dotenv import load_dotenv
from langgraph_chatbot import build_chatbot_graph

# Load environment variables
load_dotenv()

def visualize_graph():
    """Generate and save the LangGraph visualization"""
    print("Building LangGraph workflow...")

    # Build the graph
    graph = build_chatbot_graph()

    # Generate visualization
    print("Generating visualization...\n")

    # Save Mermaid text
    try:
        mermaid_diagram = graph.get_graph().draw_mermaid()

        output_file = "langgraph_workflow_mermaid.txt"
        with open(output_file, 'w') as f:
            f.write(mermaid_diagram)

        print(f"✅ Mermaid diagram saved to: {output_file}")
        print("   View at: https://mermaid.live/\n")

    except Exception as e:
        print(f"❌ Error generating Mermaid diagram: {str(e)}\n")

    # Try to generate PNG using draw_mermaid_png()
    try:
        print("Generating PNG image...")
        png_data = graph.get_graph().draw_mermaid_png()

        output_png = "langgraph_workflow.png"
        with open(output_png, 'wb') as f:
            f.write(png_data)

        print(f"✅ PNG diagram saved to: {output_png}\n")

    except Exception as e:
        print(f"⚠️ PNG generation via draw_mermaid_png() failed: {str(e)}")
        print("   Trying alternative method...\n")

        # Alternative: Use requests to convert Mermaid to PNG via API
        try:
            import requests
            import base64

            mermaid_diagram = graph.get_graph().draw_mermaid()

            # Encode mermaid diagram
            graphbytes = mermaid_diagram.encode("utf8")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")

            # Use Mermaid.ink API to render
            url = f"https://mermaid.ink/img/{base64_string}"

            print("Fetching PNG from Mermaid.ink API...")
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                output_png = "langgraph_workflow.png"
                with open(output_png, 'wb') as f:
                    f.write(response.content)

                print(f"✅ PNG diagram saved to: {output_png}\n")
            else:
                print(f"❌ API request failed with status {response.status_code}\n")

        except ImportError:
            print("⚠️ 'requests' library not installed")
            print("   Install: pip install requests\n")
        except Exception as api_error:
            print(f"❌ Alternative PNG generation failed: {str(api_error)}\n")

    # Try to generate SVG
    try:
        import requests
        import base64

        mermaid_diagram = graph.get_graph().draw_mermaid()

        # Encode mermaid diagram
        graphbytes = mermaid_diagram.encode("utf8")
        base64_bytes = base64.b64encode(graphbytes)
        base64_string = base64_bytes.decode("ascii")

        # Use Mermaid.ink API to render SVG
        url = f"https://mermaid.ink/svg/{base64_string}"

        print("Fetching SVG from Mermaid.ink API...")
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            output_svg = "langgraph_workflow.svg"
            with open(output_svg, 'wb') as f:
                f.write(response.content)

            print(f"✅ SVG diagram saved to: {output_svg}\n")
        else:
            print(f"⚠️ SVG API request failed with status {response.status_code}\n")

    except ImportError:
        print("⚠️ 'requests' library not installed for SVG generation\n")
    except Exception as svg_error:
        print(f"⚠️ SVG generation failed: {str(svg_error)}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  LANGGRAPH VISUALIZATION TOOL")
    print("="*60 + "\n")

    visualize_graph()
