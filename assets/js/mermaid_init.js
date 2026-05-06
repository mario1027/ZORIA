/**
 * mermaid_init.js
 * Inicializa y re-renderiza Mermaid.js automáticamente después de cada
 * actualización del DOM por Dash (navegación entre páginas, callbacks, etc.)
 * Además inyecta botones de pantalla completa en cada tarjeta de diagrama.
 */

(function () {
    'use strict';

    const MERMAID_CONFIG = {
        startOnLoad: false,
        theme: 'base',
        themeVariables: {
            primaryColor: '#3b82f6',
            primaryTextColor: '#0f172a',
            primaryBorderColor: '#2563eb',
            lineColor: '#64748b',
            secondaryColor: '#f0f9ff',
            tertiaryColor: '#f1f5f9',
            background: '#ffffff',
            mainBkg: '#eff6ff',
            nodeBorder: '#3b82f6',
            clusterBkg: '#f0f9ff',
            clusterBorder: '#93c5fd',
            titleColor: '#1e40af',
            edgeLabelBackground: '#f1f5f9',
            fontFamily: 'Inter, system-ui, sans-serif',
            fontSize: '14px',
        },
        flowchart: {
            curve: 'basis',
            htmlLabels: true,
            padding: 20,
            nodeSpacing: 50,
            rankSpacing: 60,
        },
        sequence: {
            diagramMarginX: 24,
            diagramMarginY: 20,
            actorMargin: 80,
            width: 180,
            height: 52,
            boxMargin: 10,
            noteMargin: 14,
            messageMargin: 44,
        },
        securityLevel: 'loose',
    };

    let mermaidReady = false;
    let pendingRender = false;

    /* ── Esperar a que window.mermaid esté disponible ── */
    function waitForMermaid(callback, attempts) {
        attempts = attempts || 0;
        if (typeof window.mermaid !== 'undefined') {
            callback();
        } else if (attempts < 80) {
            setTimeout(function () { waitForMermaid(callback, attempts + 1); }, 200);
        }
    }

    /* ── Renderizar todos los nodos .mermaid no procesados ── */
    function renderDiagrams() {
        if (!mermaidReady) { pendingRender = true; return; }

        var nodes = document.querySelectorAll('.mermaid:not([data-processed="true"])');
        if (nodes.length === 0) return;

        nodes.forEach(function (el) {
            if (!el.getAttribute('data-source')) {
                el.setAttribute('data-source', el.textContent.trim());
            } else {
                el.textContent = el.getAttribute('data-source');
                el.removeAttribute('data-processed');
            }
        });

        try {
            window.mermaid.run({ nodes: Array.from(nodes) });
        } catch (e) {
            console.warn('[ZORIA Mermaid] render error:', e);
        }

        /* Inyectar botones fullscreen después del render ─────────────────── */
        setTimeout(addFullscreenButtons, 400);
    }

    /* ── Inyectar botón fullscreen en cada .diagram-card ── */
    function addFullscreenButtons() {
        document.querySelectorAll('.diagram-card').forEach(function (card) {
            var header = card.querySelector('.diagram-header');
            var canvas = card.querySelector('.diagram-canvas');
            if (!header || !canvas) return;
            if (header.querySelector('.diagram-fullscreen-btn')) return; /* ya existe */

            var btn = document.createElement('button');
            btn.className = 'diagram-fullscreen-btn';
            btn.title = 'Pantalla completa';
            btn.innerHTML = '<i class="fas fa-expand"></i>';

            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var isFs = document.fullscreenElement === canvas ||
                           document.webkitFullscreenElement === canvas;
                if (isFs) {
                    /* Salir */
                    (document.exitFullscreen || document.webkitExitFullscreen
                        || function(){}).call(document);
                } else {
                    /* Entrar */
                    var req = canvas.requestFullscreen || canvas.webkitRequestFullscreen;
                    if (req) req.call(canvas);
                }
            });

            /* Actualizar icono al cambiar estado ────────────────────────── */
            function syncIcon() {
                var active = document.fullscreenElement === canvas ||
                             document.webkitFullscreenElement === canvas;
                btn.innerHTML = active
                    ? '<i class="fas fa-compress"></i>'
                    : '<i class="fas fa-expand"></i>';
                btn.title = active ? 'Salir de pantalla completa' : 'Pantalla completa';
            }
            document.addEventListener('fullscreenchange', syncIcon);
            document.addEventListener('webkitfullscreenchange', syncIcon);

            header.appendChild(btn);
        });
    }

    /* ── Inicialización ── */
    function init() {
        waitForMermaid(function () {
            window.mermaid.initialize(MERMAID_CONFIG);
            mermaidReady = true;
            renderDiagrams();
            if (pendingRender) { pendingRender = false; renderDiagrams(); }
        });
    }

    /* MutationObserver — re-render cuando Dash inyecta contenido nuevo ──── */
    var debounceTimer = null;
    var observer = new MutationObserver(function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(renderDiagrams, 120);
    });
    observer.observe(document.body, { childList: true, subtree: true });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
