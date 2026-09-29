/**
 * Inicializa window.dash_clientside antes de dash_renderer.
 * El namespace _dashprivate_clientside_funcs se registra en scripts inline
 * del bloque _dash-config; este stub evita dc[namespace] === undefined.
 */
(function () {
  'use strict';
  var dc = window.dash_clientside || {};
  window.dash_clientside = dc;
  if (!dc._dashprivate_clientside_funcs) {
    dc._dashprivate_clientside_funcs = {};
  }
})();
