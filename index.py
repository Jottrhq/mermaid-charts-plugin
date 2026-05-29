from mermaid_charts import renderer


def register(api):
    api.register_markdown_extension({
        "id": "mermaid-charts.renderer",
        "title": "Mermaid Chart Renderer",
        "process_html": renderer.process_html,
        "head_html": renderer.head_html,
        "style_html": renderer.style_html,
        "body_html": renderer.body_html,
    })
    api.register_editor_extension({
        "id": "mermaid-charts.renderer",
        "title": "Mermaid Chart Renderer",
        "module": "mermaid_charts.renderer"
    })
