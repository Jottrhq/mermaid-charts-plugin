import html
import json
import re
from pathlib import Path


def process_html(body_html, context=None):
    def replace_mermaid(match):
        attributes = match.group(1) or ""
        diagram_source = html.unescape(match.group(2)).strip()
        if "language-mermaid" not in attributes and "mermaid" not in attributes:
            return match.group(0)
        return render_mermaid_block(diagram_source)

    return re.sub(r'<pre><code([^>]*)>(.*?)</code></pre>', replace_mermaid, body_html, flags=re.DOTALL)


def render_mermaid_block(diagram_source):
    escaped_source = html.escape(diagram_source)
    return '<div class="mermaid-block"><div class="mermaid">{}</div></div>'.format(escaped_source)


def head_html(context=None):
    return '<script>\n{}\n</script>'.format(load_bundled_script())


def style_html(context=None):
    return """
                .mermaid {
                    background: #ffffff;
                    border: 1px solid #d0d7de;
                    border-radius: 6px;
                    margin: 1em 0;
                    padding: 12px;
                    overflow-x: auto;
                    text-align: center;
                }
                .mermaid-svg {
                    display: block;
                    height: auto;
                    max-width: 100%;
                    min-width: 220px;
                }
                .mermaid svg {
                    display: inline-block;
                    max-width: 100%;
                }
                .mermaid-error {
                    color: #b42318;
                    font-family: "DejaVu Sans Mono", "Consolas", monospace;
                    text-align: start;
                    white-space: pre-wrap;
                }
    """


def body_html(context=None):
    render_error = json.dumps("Mermaid render error:")
    runtime_error = json.dumps("Mermaid runtime could not be loaded.")
    return f"""
            <script>
                async function renderMermaidDiagrams() {{
                    if (!window.mermaid) {{
                        document.querySelectorAll('.mermaid').forEach(function (diagram) {{
                            diagram.classList.add('mermaid-error');
                            diagram.textContent = {runtime_error} + '\n\n' + diagram.textContent;
                        }});
                        return;
                    }}

                    try {{
                        if (window.jottrMermaidRendering) {{
                            return;
                        }}
                        window.jottrMermaidRendering = true;
                        mermaid.initialize({{
                            startOnLoad: false,
                            securityLevel: 'loose',
                            theme: 'default'
                        }});

                        function renderDiagram(renderId, source, diagram) {{
                            return new Promise(function (resolve, reject) {{
                                try {{
                                    if (mermaid.render.length >= 3) {{
                                        mermaid.render(renderId, source, function (svg, bindFunctions) {{
                                            resolve({{
                                                svg: svg,
                                                bindFunctions: bindFunctions
                                            }});
                                        }}, diagram);
                                        return;
                                    }}

                                    Promise.resolve(mermaid.render(renderId, source)).then(function (result) {{
                                        if (typeof result === 'string') {{
                                            resolve({{
                                                svg: result,
                                                bindFunctions: null
                                            }});
                                        }} else {{
                                            resolve(result);
                                        }}
                                    }}).catch(reject);
                                }} catch (error) {{
                                    reject(error);
                                }}
                            }});
                        }}

                        var diagrams = Array.prototype.slice.call(document.querySelectorAll('.mermaid'));
                        diagrams = diagrams.filter(function (diagram) {{
                            return diagram.dataset.rendered !== 'true' && diagram.dataset.processed !== 'true';
                        }});

                        if (diagrams.length && typeof mermaid.run === 'function') {{
                            try {{
                                await mermaid.run({{
                                    nodes: diagrams,
                                    suppressErrors: false
                                }});
                                diagrams.forEach(function (diagram) {{
                                    diagram.dataset.rendered = 'true';
                                    diagram.classList.remove('mermaid-error');
                                }});
                            }} catch (error) {{
                                diagrams.forEach(function (diagram) {{
                                    diagram.classList.add('mermaid-error');
                                    diagram.textContent = {render_error} + ' ' + error.message + '\n\n' + diagram.textContent;
                                }});
                            }}
                        }} else {{
                            for (var index = 0; index < diagrams.length; index += 1) {{
                                var diagram = diagrams[index];
                                var source = diagram.textContent;
                                var renderId = 'jottr-mermaid-' + Date.now() + '-' + index;
                                try {{
                                    var result = await renderDiagram(renderId, source, diagram);
                                    diagram.innerHTML = result.svg;
                                    diagram.dataset.rendered = 'true';
                                    diagram.classList.remove('mermaid-error');
                                    if (result.bindFunctions) {{
                                        result.bindFunctions(diagram);
                                    }}
                                }} catch (error) {{
                                    diagram.classList.add('mermaid-error');
                                    diagram.textContent = {render_error} + ' ' + error.message + '\n\n' + source;
                                }}
                            }}
                        }}
                    }} catch (error) {{
                        console.error('Mermaid render failed', error);
                    }} finally {{
                        window.jottrMermaidRendering = false;
                    }}
                }}

                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', renderMermaidDiagrams);
                }} else {{
                    renderMermaidDiagrams();
                }}

                window.addEventListener('load', renderMermaidDiagrams);
            </script>
    """


def load_bundled_script():
    mermaid_path = Path(__file__).resolve().parent / 'vendor' / 'mermaid.min.js'
    try:
        script_content = mermaid_path.read_text(encoding='utf-8')
    except OSError:
        script_content = ""
    return script_content.replace("</script", "<\\/script")
