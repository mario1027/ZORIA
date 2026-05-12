/**
 * Dynamic Favicon — switches between dark/light logo based on data-theme
 * Dark mode → logo-white.png (blanco, visible sobre tab oscuro)
 * Light mode → logo.png (oscuro, visible sobre tab claro)
 */
(function () {
    'use strict';

    var FAVICON_DARK  = '/assets/logo-white.png';
    var FAVICON_LIGHT = '/assets/logo.png';

    function applyFavicon(theme) {
        var href = theme === 'light' ? FAVICON_LIGHT : FAVICON_DARK;
        var link = document.querySelector('link[rel~="icon"]');
        if (!link) {
            link = document.createElement('link');
            link.rel = 'icon';
            link.type = 'image/png';
            document.head.appendChild(link);
        }
        if (link.href !== href) {
            link.href = href;
        }
    }

    function init() {
        var html = document.documentElement;
        applyFavicon(html.getAttribute('data-theme') || 'dark');

        // Observar cambios en data-theme
        var observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (m) {
                if (m.attributeName === 'data-theme') {
                    applyFavicon(html.getAttribute('data-theme'));
                }
            });
        });
        observer.observe(html, { attributes: true, attributeFilter: ['data-theme'] });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
