// Renders the Mermaid diagrams in Jottr's Markdown preview.
//
// Jottr runs this again after every render it swaps into the page, so each
// run only renders diagrams it has not seen. Diagrams whose source is
// unchanged get their cached SVG back straight away, before the page paints,
// so editing text around a diagram never makes it flicker.
(function () {
    'use strict';

    var CACHE_LIMIT = 50;

    if (!window.jottrMermaid) {
        window.jottrMermaid = {
            cache: new Map(),
            counter: 0,
            initialized: false
        };
    }
    var state = window.jottrMermaid;

    function remember(source, svg) {
        state.cache.delete(source);
        state.cache.set(source, svg);
        if (state.cache.size > CACHE_LIMIT) {
            state.cache.delete(state.cache.keys().next().value);
        }
    }

    function showError(diagram, source, message) {
        diagram.classList.add('mermaid-error');
        diagram.textContent = message + '\n\n' + source;
    }

    function render(id, source) {
        // Mermaid 10 returns a promise of {svg}; Mermaid 9 has renderAsync and
        // a render that returns the SVG itself.
        if (typeof mermaid.renderAsync === 'function') {
            return mermaid.renderAsync(id, source);
        }
        return Promise.resolve(mermaid.render(id, source));
    }

    function renderDiagram(diagram) {
        var source = diagram.textContent;
        diagram.dataset.rendered = 'true';

        var cached = state.cache.get(source);
        if (cached !== undefined) {
            diagram.innerHTML = cached;
            return;
        }

        state.counter += 1;
        var id = 'jottr-mermaid-' + state.counter;
        render(id, source).then(function (result) {
            var svg = typeof result === 'string' ? result : result.svg;
            remember(source, svg);
            diagram.innerHTML = svg;
            diagram.classList.remove('mermaid-error');
        }).catch(function (error) {
            showError(diagram, source, 'Mermaid render error: ' + (error && error.message ? error.message : error));
        }).finally(function () {
            // Mermaid 9 leaves its scratch element behind when a diagram fails.
            var scratch = document.getElementById('d' + id);
            if (scratch) {
                scratch.remove();
            }
        });
    }

    var diagrams = document.querySelectorAll('.mermaid:not([data-rendered])');
    if (!window.mermaid) {
        Array.prototype.forEach.call(diagrams, function (diagram) {
            showError(diagram, diagram.textContent, 'Mermaid runtime could not be loaded.');
        });
        return;
    }

    if (!state.initialized) {
        // Like Zettlr: render only when asked, and treat diagrams from
        // documents as untrusted (no scripts, click handlers, or raw HTML).
        mermaid.initialize({
            startOnLoad: false,
            securityLevel: 'strict',
            theme: 'default'
        });
        state.initialized = true;
    }
    Array.prototype.forEach.call(diagrams, renderDiagram);
})();
