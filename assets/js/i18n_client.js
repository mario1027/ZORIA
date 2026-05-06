/**
 * assets/js/i18n_client.js  –  ZORIA Client-side i18n  (v3 – robust)
 *
 * Flujo principal (Dash callbacks):
 *   lang-store (localStorage) → serve_translations → lang-translations-store
 *   → apply_i18n clientside → ZORIA_I18N.apply(lang, dict) → DOM
 *
 * Flujo de recuperación instantánea (sin esperar callbacks):
 *   - Al cargar el script: lee lang de localStorage YA, restaura traducciones
 *     de sessionStorage YA → aplica antes de que Dash responda.
 *   - Al navegar (pushState / popstate): multi-retry a 200/500/900 ms.
 *   - MutationObserver: doble-pass (200 ms debounce + retry +400 ms).
 *   - pageshow: para restore de bfcache.
 *   - Retries en DOMContentLoaded: 600 ms y 1500 ms.
 */
(function () {
  'use strict';

  /* ── 1. Estado inicial – leer desde localStorage SIN esperar Dash ────────── */
  window.ZORIA_TRANSLATIONS = window.ZORIA_TRANSLATIONS || {};
  window.ZORIA_I18N = window.ZORIA_I18N || {};
  if (typeof window.ZORIA_I18N.apply !== 'function') {
    window.ZORIA_I18N.apply = function () {};
  }

  /* ── ANTI-FOUC: ocultar contenido AHORA si el idioma no es español ───────── */
  /* Esto se ejecuta antes de que el DOM esté listo, así que usamos <html>.    */
  var _earlyLang = 'es';
  try {
    var _earlyRaw = localStorage.getItem('lang-store');
    if (_earlyRaw) _earlyLang = JSON.parse(_earlyRaw) || 'es';
  } catch (e) {}
  var _needsBlock = (_earlyLang !== 'es');
  if (_needsBlock) {
    document.documentElement.classList.add('i18n-pending');
  }
  /* Safety net: si en 1200 ms no se quitó la clase, la quitamos solos */
  var _fouc_timeout = _needsBlock ? setTimeout(function () {
    document.documentElement.classList.remove('i18n-pending');
  }, 1200) : null;

  var _literalToKey = {
    'Minimizar': 'ui.minimize',
    'Maximizar': 'ui.maximize',
    'Maximizar/Restaurar': 'ui.max_restore',
    'Cerrar (Esc)': 'ui.close_esc',
    'Cambiar tema': 'ui.change_theme',
    'Cambiar tema de gráficos': 'ui.change_chart_theme',
    'Conexión Rápida': 'ui.quick_connect',
    'Desconectar': 'ui.disconnect',
    'Conectado': 'conn.connected',
    'Desconectado': 'conn.disconnected',
    'Buscando...': 'conn.searching',
    'Sin puertos USB': 'conn.no_ports',
    'No detectado': 'conn.not_detected',
    'Sin respuesta': 'conn.no_response',
    'Ocupado': 'conn.busy',
    'Puerto cerrado': 'conn.port_closed',
    'Error': 'conn.error',
    'Abrir Terminal CLI (Alt+T)': 'ui.open_terminal',
    'Abrir menú de navegación': 'ui.open_menu',
    'Cerrar menú (clickear afuera también cierra)': 'ui.close_menu',
    'Ir a Dashboard': 'ui.go_dashboard',
    'Volver al dashboard principal': 'ui.back_dashboard',
    'Language / Idioma': 'ui.lang_picker',
    'Seleccionar puerto...': 'ui.select_port',
    'Puerto Manual': 'ui.manual_port',
    'Buscando dispositivo...': 'ui.searching_device',
    'Puerto:': 'ui.port_prefix',
    'Auto': 'ui.auto',
    'Ej: 0.2, 1.0': 'ui.example_value',
    'Frecuencia (Hz)': 'ui.freq_hz',
    "Parte Real Z' (Ω)": 'ui.real_z',
    "Parte Imaginaria -Z'' (Ω)": 'ui.imag_z',
    'Error en el cálculo': 'ui.calc_error',
    'Error en el cálculo de impedancia': 'ui.calc_error_imp',
    'RLC Circuit Simulator': 'ui.rlc_sim_title',
    'Selección de Circuito': 'ui.circuit_select',
    'Tipo de Circuito': 'ui.circuit_type',
    'Fórmula:': 'ui.formula',
    'Rango de Frecuencias': 'ui.range_freq',
    'Frecuencia Inicial': 'ui.freq_start',
    'Frecuencia Final': 'ui.freq_end',
    'Número de Puntos': 'ui.num_points',
    'Información de Impedancia': 'ui.info_impedance',
    'Resistencia (R)': 'ui.resistance_r',
    'Inductancia (L)': 'ui.inductance_l',
    'Capacitancia (C)': 'ui.capacitance_c',
    'Ejemplo: 1000 = 1 kΩ | Rango: 1 Ω - 10 MΩ': 'ui.sample_res',
    'Ejemplo: 0.001 = 1 mH | Rango: 1 nH - 100 H': 'ui.sample_ind',
    'Ejemplo: 0.000001 = 1 µF | Rango: 1 pF - 1 F': 'ui.sample_cap',
    'ADMX2001 — CLI': 'ui.terminal_title',
    'Esperando conexión con ADMX2001...': 'ui.waiting_connection',
    'Comandos disponibles:': 'ui.available_commands',
    'Atajos:': 'ui.shortcuts_label',
    ' Abrir/Cerrar  ': 'ui.open_close',
    ' Historial': 'ui.history',
    'Terminal': 'footer.terminal',
    'Cerrar': 'footer.close',
    'Limpiar': 'footer.clear',
    'Exportar': 'ui.export',
    /* ── Pestañas de documentación (label es string plano; el TreeWalker las traduce) ── */
    '\ud83d\ude80 Inicio R\u00e1pido': 'doc.tab.start',
    '\ud83e\uddee Matem\u00e1tica':    'doc.tab.math',
    '\u2696\ufe0f Calibraci\u00f3n':   'doc.tab.calibration',
    '\ud83e\udd1d Contribuir':      'doc.tab.contribute',
    /* ── Encabezados H3 de documentaci\u00f3n ─────────────────────────────────── */
    'DOCUMENTACI\u00d3N OFICIAL':                              'doc.hero.badge',
    'Gu\u00eda ZORIA':                                         'doc.hero.title',
    'Inicio R\u00e1pido - Five Simple Steps':                  'doc.section.start',
    'Especificaciones de Hardware':                       'doc.section.hardware',
    'Gu\u00eda de Software ZORIA':                            'doc.section.software',
    'Matem\u00e1tica Background: Hardware + Software':        'doc.section.math',
    'Procedimiento de Calibraci\u00f3n OSL':                  'doc.section.calibration',
    'Terminal CLI - Interfaz de L\u00ednea de Comandos':      'doc.section.cli',
    'Actualizaci\u00f3n de Firmware ADMX2001B':               'doc.section.firmware',
    '\u00bfQu\u00e9 es ZORIA?':                                      'doc.section.overview',
    'Contribuir a ZORIA':                                 'doc.section.contribute'
  };

  var _autoCacheByLang = {};
  var _autoInflight = {};
  var _docOriginalTextByNode = new Map();

  function _isDocumentationPath() {
    return /\/(documentaci[oó]n|documentation)/.test(window.location.pathname);
  }

  function _getLiteralFallbackRoot() {
    if (_isDocumentationPath()) {
      return document.querySelector('.doc-tabs-content') ||
             document.getElementById('doc-tabs') ||
             document.body;
    }
    return document.body;
  }

  function _restoreDocumentationOriginals(root) {
    _docOriginalTextByNode.forEach(function (originalText, textNode) {
      if (!textNode || !textNode.parentElement || !document.contains(textNode)) {
        _docOriginalTextByNode.delete(textNode);
        return;
      }
      if (root && !root.contains(textNode)) return;
      textNode.nodeValue = originalText;
    });
  }

  function _loadAutoCache(lang) {
    if (_autoCacheByLang[lang]) return _autoCacheByLang[lang];
    var cache = {};
    try {
      var raw = sessionStorage.getItem('zoria-auto-i18n-' + lang);
      if (raw) cache = JSON.parse(raw) || {};
    } catch (e) {}
    _autoCacheByLang[lang] = cache;
    return cache;
  }

  function _saveAutoCache(lang) {
    try {
      sessionStorage.setItem('zoria-auto-i18n-' + lang, JSON.stringify(_autoCacheByLang[lang] || {}));
    } catch (e) {}
  }

  function _shouldAutoTranslate(text) {
    if (!text) return false;
    var t = text.trim();
    if (!t) return false;
    if (t.length < 3) return false;
    if (/^[0-9\s+\-*/().,%°Ω=:_\[\]{}<>]+$/.test(t)) return false;
    if (/^[A-Za-z0-9_\-]+$/.test(t) && t.length < 10) return false;
    return /[A-Za-zÁÉÍÓÚáéíóúÑñ]/.test(t);
  }

  function _autoTranslateLiteral(text, lang, onDone) {
    if (!text || lang === 'es') return;
    var source = text.trim();
    if (!_shouldAutoTranslate(source)) return;

    var cache = _loadAutoCache(lang);
    if (cache[source]) {
      onDone(cache[source]);
      return;
    }

    var key = lang + '|' + source;
    if (_autoInflight[key]) {
      _autoInflight[key].push(onDone);
      return;
    }
    _autoInflight[key] = [onDone];

    var url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=es&tl=' + encodeURIComponent(lang) + '&dt=t&q=' + encodeURIComponent(source);
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (payload) {
        var translated = source;
        try {
          translated = (payload && payload[0] || []).map(function (p) { return p[0] || ''; }).join('') || source;
        } catch (e) {}
        _autoCacheByLang[lang][source] = translated;
        _saveAutoCache(lang);
        (_autoInflight[key] || []).forEach(function (cb) { cb(translated); });
        delete _autoInflight[key];
      })
      .catch(function () {
        (_autoInflight[key] || []).forEach(function () {});
        delete _autoInflight[key];
      });
  }

  var _currentLang = 'es';
  try {
    var _lsLang = localStorage.getItem('lang-store');
    if (_lsLang) { _currentLang = JSON.parse(_lsLang) || 'es'; }
  } catch (e) { /* sin acceso a localStorage */ }

  /* Restaura traducciones del caché de sesión (sobrevive F5 y cambio de página) */
  try {
    var _cached = sessionStorage.getItem('zoria-i18n-' + _currentLang);
    if (_cached) { window.ZORIA_TRANSLATIONS = JSON.parse(_cached); }
  } catch (e) {}

  /* ── 2. Función principal ─────────────────────────────────────────────────── */
  function applyTranslations(lang, translations) {
    if (!lang) return;
    _currentLang = lang;

    if (translations && Object.keys(translations).length > 0) {
      window.ZORIA_TRANSLATIONS = translations;
      /* Cuando Dash provee traducciones frescas, cancelar todos los timers pendientes
         del MutationObserver y onDomReady para que no pisen el idioma correcto */
      clearTimeout(_debounceTimer);
      clearTimeout(_retryTimer);
      clearTimeout(_domReadyRetry1);
      clearTimeout(_domReadyRetry2);      /* Cachea en sessionStorage para el siguiente render / recarga */
      try {
        sessionStorage.setItem('zoria-i18n-' + lang, JSON.stringify(translations));
        /* Limpia caches de otros idiomas para no desperdiciar espacio */
        ['es','en','pt','zh','ru','de'].forEach(function (c) {
          if (c !== lang) sessionStorage.removeItem('zoria-i18n-' + c);
        });
      } catch (e) {}
    }

    var dict = window.ZORIA_TRANSLATIONS;
    if (!dict || Object.keys(dict).length === 0) return;

    /* Levantar el bloqueo anti-FOUC SOLO después de que React ya renderizó.
       _reactRendered se marca a true en el MutationObserver (primer render de Dash).
       Excepción: si Dash nos envió traducciones frescas del servidor (_isFromDash),
       también lo levantamos (el server round-trip es más lento que React → página
       ya renderizada). Así no revelamos el body con el HTML en español antes de que
       las traducciones se hayan aplicado al contenido real de la página. */
    var _isFromDash = !!(translations && Object.keys(translations).length > 0);
    if ((_reactRendered || _isFromDash) && document.documentElement.classList.contains('i18n-pending')) {
      clearTimeout(_fouc_timeout);
      document.documentElement.classList.remove('i18n-pending');
    }

    /* ── Desconectar el observer mientras mutamos el DOM para evitar el feedback
       loop (MutationObserver → applyTranslations → MutationObserver…) ── */
    if (_observer) _observer.disconnect();

    /* ── Aplica textContent / placeholder en [data-i18n] ── */
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key   = el.getAttribute('data-i18n');
      var value = dict[key];
      if (value === undefined) return;

      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.setAttribute('placeholder', value);
      } else {
        var target = el.querySelector('[data-i18n-text]') || el;
        if (!target.querySelector('svg') && !target.querySelector('i')) {
          target.textContent = value;
        } else {
          Array.from(target.childNodes).forEach(function (node) {
            if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
              node.textContent = ' ' + value;
            }
          });
        }
      }
    });

    /* ── Aplica title en [data-i18n-title] ── */
    document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
      var key   = el.getAttribute('data-i18n-title');
      var value = dict[key];
      if (value !== undefined) el.setAttribute('title', value);
    });

    _applyLiteralFallback(dict);

    /* ── Marca botón activo en language picker (navbar) ── */
    /* Las .lang-card del config page las gestiona exclusivamente el callback
       cfg-cards-sync de Dash para reflejar la selección PENDIENTE (no guardada).
       Si applyTranslations las tocara, pisaría la tarjeta que el usuario acaba
       de seleccionar (usando el idioma guardado en lugar del pendiente). */
    document.querySelectorAll('.lang-btn').forEach(function (btn) {
      btn.classList.toggle('lang-btn--active', btn.getAttribute('data-lang') === lang);
    });

    /* ── _syncThemeButtons / _syncAutoconnButtons se llaman sólo desde los
       callbacks de Dash (cfg-cards-sync). Aquí NO las llamamos para no pisar
       el estado pendiente que el usuario puede haber elegido en la config. ── */
    _bindSidebarConfigButton();

    /* ── Atributo lang en <html> ── */
    document.documentElement.setAttribute('lang', lang);

    /* ── Placeholder del terminal ── */
    var termInput = document.getElementById('command-input');
    if (termInput && dict['terminal.placeholder']) {
      termInput.setAttribute('placeholder', dict['terminal.placeholder']);
    }

    /* ── Evento personalizado para módulos externos ── */
    document.dispatchEvent(new CustomEvent('zoria:langchange', { detail: { lang: lang } }));

    /* Reactiva el observer ahora que todos los cambios de DOM están hechos */
    startObserver();
  }

  function _translateLiteralText(value, dict) {
    if (!value) return null;
    var key = _literalToKey[value.trim()];
    if (!key) return null;
    return dict[key] || null;
  }

  function _applyLiteralFallback(dict) {
    var root = _getLiteralFallbackRoot();

    /* Solo aplicar el fallback literal cuando el idioma NO es español.
       En español el HTML ya está correcto; el auto-translate está desactivado
       para ese idioma de todas formas. El fallback literal también se desactiva
       completamente: los textos que no tienen [data-i18n] se dejan intactos
       para evitar que el walker asincrónico pise texto ya traducido correctamente. */
    if (_currentLang === 'es') {
      if (_isDocumentationPath()) _restoreDocumentationOriginals(root);
      return;
    }

    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    var node;
    var _docNewFetches = 0; /* contador de nuevas peticiones de auto-translate por llamada */
    while ((node = walker.nextNode())) {
      if (!node.parentElement) continue;
      var parentTag = node.parentElement.tagName;
      if (parentTag === 'SCRIPT' || parentTag === 'STYLE' || parentTag === 'CODE' || parentTag === 'PRE') continue;
      /* Saltar nodos dentro de elementos que ya tienen [data-i18n] — ya los
         procesamos arriba y volver a tocarlos causa el loop de mutations */
      if (node.parentElement.closest('[data-i18n]')) continue;
      var raw = node.nodeValue;
      if (!raw || !raw.trim()) continue;
      if (_isDocumentationPath() && !_docOriginalTextByNode.has(node)) {
        _docOriginalTextByNode.set(node, raw);
      }
      var sourceRaw = _isDocumentationPath() ? (_docOriginalTextByNode.get(node) || raw) : raw;
      var translated = _translateLiteralText(sourceRaw, dict);
      if (translated) {
        var lead = sourceRaw.match(/^\s*/)[0];
        var tail = sourceRaw.match(/\s*$/)[0];
        node.nodeValue = lead + translated + tail;
      }
      /* Auto-translate asincrónico: activo solo en /documentacion.
         Usa closures por nodo para aplicar la traducción directamente al nodo
         sin re-ejecutar applyTranslations (evita el bucle infinito). */
      if (!translated && _isDocumentationPath()) {
        var _docCache = _loadAutoCache(_currentLang);
        var _trimmed = sourceRaw.trim();
        if (_docCache[_trimmed]) {
          var _lead = sourceRaw.match(/^\s*/)[0];
          var _tail = sourceRaw.match(/\s*$/)[0];
          node.nodeValue = _lead + _docCache[_trimmed] + _tail;
        } else if (_docNewFetches < 80) {
          var _wasInflight = !!_autoInflight[_currentLang + '|' + _trimmed];
          (function (capturedNode, capturedTrimmed, capturedLang, capturedSource) {
            _autoTranslateLiteral(capturedTrimmed, capturedLang, function (result) {
              if (result && _currentLang === capturedLang && document.contains(capturedNode)) {
                var _l = capturedSource.match(/^\s*/)[0];
                var _t = capturedSource.match(/\s*$/)[0];
                capturedNode.nodeValue = _l + result + _t;
              }
            });
          })(node, _trimmed, _currentLang, sourceRaw);
          if (!_wasInflight) _docNewFetches++;
        }
      }
    }

    document.querySelectorAll('[title]').forEach(function (el) {
      if (el.closest('[data-i18n-title]')) return;
      var translated = _translateLiteralText(el.getAttribute('title') || '', dict);
      if (translated) el.setAttribute('title', translated);
    });

    document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(function (el) {
      if (el.hasAttribute('data-i18n')) return;
      var translated = _translateLiteralText(el.getAttribute('placeholder') || '', dict);
      if (translated) el.setAttribute('placeholder', translated);
    });
  }

  function _showConnectModalNow() {
    if (window.location.pathname !== '/') return;

    var modal = document.getElementById('connect-modal');
    if (!modal) return;

    modal.style.display = 'flex';

    setTimeout(function () {
      if (window.DraggableWindows) {
        if (!window.DraggableWindows.isInitialized('connect-modal')) {
          window.DraggableWindows.init('connect-modal', 'connect-modal-header', {width: 380, height: 420});
        }
        window.DraggableWindows.show('connect-modal');
      }
    }, 80);
  }

  function _bindSidebarConfigButton() {
    var btn = document.getElementById('sidebar-config-btn');
    if (!btn || btn.dataset.zoriaConnectBound === '1') return;
    btn.dataset.zoriaConnectBound = '1';

    // NO usar capture/stopPropagation: Dash debe ver el click para actualizar n_clicks.
    // El clientside callback de Dash abre el modal via el prop de React (no JS directo),
    // lo que permite que el cierre funcione correctamente.
    btn.addEventListener('click', function (e) {
      if (window.location.pathname !== '/') {
        e.preventDefault();
        window.location.href = '/';
      }
      // Si ya estamos en '/', Dash maneja la apertura vía sidebar-config-btn.n_clicks
    });
  }

  /* ── 3. Sincronizar botones de tema ─────────────────────────────────────── */
  function _syncThemeButtons() {
    var theme = null;
    try { theme = JSON.parse(localStorage.getItem('theme-store')); } catch (e) {}
    if (!theme) return;
    document.querySelectorAll('.theme-option').forEach(function (btn) {
      btn.classList.toggle('theme-option--active', btn.getAttribute('data-theme') === theme);
    });
  }

  /* ── 3b. Sincronizar botones de autoconn ────────────────────────────────── */
  function _syncAutoconnButtons() {
    var isOn = false;
    try { isOn = !!JSON.parse(localStorage.getItem('autoconn-store')); } catch (e) {}
    var btnOn  = document.getElementById('cfg-autoconn-on');
    var btnOff = document.getElementById('cfg-autoconn-off');
    if (btnOn)  btnOn.className  = isOn ? 'btn btn-sm btn-success me-2'      : 'btn btn-sm btn-outline-success me-2';
    if (btnOff) btnOff.className = isOn ? 'btn btn-sm btn-outline-secondary' : 'btn btn-sm btn-secondary';
  }

  /* ── 4. API pública ─────────────────────────────────────────────────────── */
  window.ZORIA_I18N = {
    apply  : applyTranslations,
    syncTheme: _syncThemeButtons,
    syncAutoconn: _syncAutoconnButtons,
    current: function () { return _currentLang; },
    t      : function (key) {
      return (window.ZORIA_TRANSLATIONS && window.ZORIA_TRANSLATIONS[key]) || ('[' + key + ']');
    },
  };

  /* ── 5. MutationObserver – doble-pass ──────────────────────────────────── */
  var _debounceTimer   = null;
  var _retryTimer      = null;
  var _domReadyRetry1  = null;  /* handles de los setTimeout de onDomReady */
  var _domReadyRetry2  = null;  /* son cancelados por applyTranslations(Dash) */
  var _reactRendered   = false; /* se activa en la primera mutación real de Dash */

  var _observer = new MutationObserver(function (mutations) {
    var relevant = mutations.some(function (m) {
      return Array.from(m.addedNodes).some(function (n) {
        return n.nodeType === Node.ELEMENT_NODE;
      });
    });
    if (!relevant) return;

    _reactRendered = true;  /* React ya insertó nodos → podemos levantar el bloqueo */
    clearTimeout(_debounceTimer);
    clearTimeout(_retryTimer);

    /* Debounce fijo de 200ms: seguro para cualquier tamaño de render batch */
    _debounceTimer = setTimeout(function () {
      applyTranslations(_currentLang);
      /* Segunda pasada: captura elementos que Dash renderiza en lotes tardíos */
      _retryTimer = setTimeout(function () {
        applyTranslations(_currentLang);
      }, 350);
    }, 200);
  });

  function startObserver() {
    var target = document.getElementById('page-content') ||
                 document.getElementById('_pages_content') ||
                 document.body;
    _observer.observe(target, { childList: true, subtree: true });
  }

  /* ── 6. DOMContentLoaded – aplicar en cuanto el DOM esté listo ─────────── */
  function onDomReady() {
    startObserver();
    _bindSidebarConfigButton();
    /* Aplica inmediatamente si ya tenemos traducciones del caché */
    if (Object.keys(window.ZORIA_TRANSLATIONS).length > 0) {
      applyTranslations(_currentLang);
    }
    /* Retries para capturar renders tardíos de Dash.
       Se guardan en variables para que applyTranslations(Dash) pueda cancelarlos
       si llegan traducciones frescas antes de que disparen. */
    _domReadyRetry1 = setTimeout(function () { applyTranslations(_currentLang); }, 600);
    _domReadyRetry2 = setTimeout(function () { applyTranslations(_currentLang); }, 1500);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onDomReady);
  } else {
    onDomReady();
  }

  /* ── 7. SPA navigation – multi-retry ───────────────────────────────────── */
  function _onNavigate() {
    [200, 500, 900].forEach(function (d) {
      setTimeout(function () { applyTranslations(_currentLang); }, d);
    });
  }

  var _origPushState = history && history.pushState;
  if (typeof _origPushState === 'function') {
    history.pushState = function () {
      _origPushState.apply(this, arguments);
      _onNavigate();
    };
  }

  /* Navegación con botones Atrás / Adelante */
  window.addEventListener('popstate', _onNavigate);

  /* Restauración de bfcache (pestaña congelada que vuelve) */
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) {
      setTimeout(function () { applyTranslations(_currentLang); }, 100);
    }
  });

  /* ── 8. Función registrada en window.dash_clientside para Dash ─────────── */
  window.dash_clientside = window.dash_clientside || {};
  window.dash_clientside.zoria = window.dash_clientside.zoria || {};
  window.dash_clientside.zoria.applyI18n = function (payload) {
    if (!payload) return window.dash_clientside.no_update;
    var lang = payload['_lang'];
    if (!lang) return window.dash_clientside.no_update;
    try {
      applyTranslations(lang, payload);
    } catch (e) {
      console.error('[i18n] applyI18n failed:', e);
    }
    return window.dash_clientside.no_update;
  };

})();
