import functools
import html
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


PACKAGE_DIR = Path(__file__).resolve().parent


def head_html(context=None):
    # Loaded from the plugin folder rather than inlined, so the 2.7 MB runtime
    # is not copied into every preview page.
    return '<script src="{}"></script>'.format(
        html.escape((PACKAGE_DIR / 'vendor' / 'mermaid.min.js').as_uri(), quote=True)
    )


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
    return '<script>\n{}\n</script>'.format(load_render_script())


@functools.lru_cache(maxsize=1)
def load_render_script():
    try:
        script_content = (PACKAGE_DIR / 'render.js').read_text(encoding='utf-8')
    except OSError:
        script_content = ""
    return script_content.replace("</script", "<\\/script")
