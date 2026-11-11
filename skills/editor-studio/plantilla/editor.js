// Editor Studio · movimiento de las piezas.
// Lee window.PLAN (lo escribe `armar`) y registra una sola línea de tiempo pausada.
// Todo lo visible es función del tiempo: sin azar sin semilla, sin relojes, sin repeticiones infinitas.
(function () {
  var P = window.PLAN, tl = gsap.timeline({ paused: true });
  var PERFIL = {
    suave: { entra: 0.45, sale: 0.28, ease: "power3.out", rebote: "back.out(1.25)" },
    energico: { entra: 0.32, sale: 0.22, ease: "power4.out", rebote: "back.out(1.7)" },
    sobrio: { entra: 0.6, sale: 0.35, ease: "power2.out", rebote: "power2.out" }
  };
  var M = PERFIL[P.movimiento] || PERFIL.suave;
  var W = P.W, H = P.H;

  function ver(sel, a, b) {
    tl.set(sel, { visibility: "visible" }, a);
    tl.set(sel, { visibility: "hidden" }, b);
  }
  function desde(sel, de, a, t, dur, ease) {
    var hasta = Object.assign({}, a, { duration: dur || M.entra, ease: ease || M.ease, immediateRender: false });
    tl.fromTo(sel, de, hasta, t);
  }
  function salir(sel, a, t1, dur) {
    var d = dur || M.sale;
    tl.to(sel, Object.assign({ duration: d, ease: "power2.in" }, a), Math.max(0, t1 - d));
  }
  // azar con semilla: mismas partículas en cada render
  function semilla(s) {
    var x = 0;
    for (var i = 0; i < s.length; i++) x = (x * 31 + s.charCodeAt(i)) >>> 0;
    return function () { x = (x * 1664525 + 1013904223) >>> 0; return x / 4294967296; };
  }

  // ----- cámara: zooms y panel comparten #cam -----
  var foco = P.foco;
  tl.set("#cam", { scale: 1, x: 0, y: 0 }, 0);

  P.piezas.forEach(function (p) {
    var s = "#" + p.id, i = s + " .in", t0 = p.t0, t1 = p.t1, dur = t1 - t0;
    switch (p.tipo) {
      case "titulo":
        ver(s, t0, t1);
        desde(i, { opacity: 0, y: 46, scale: 0.96 }, { opacity: 1, y: 0, scale: 1 }, t0, M.entra, M.rebote);
        salir(i, { opacity: 0, y: -24 }, t1);
        break;
      case "rotulo":
        ver(s, t0, t1);
        desde(i, { opacity: 0, x: -70 }, { opacity: 1, x: 0 }, t0);
        desde(s + " .barra", { scaleY: 0 }, { scaleY: 1 }, t0 + 0.08, 0.35, "power3.out");
        salir(i, { opacity: 0, x: -40 }, t1);
        break;
      case "fuente":
        ver(s, t0, t1);
        desde(i, { opacity: 0, y: 18 }, { opacity: 1, y: 0 }, t0, 0.3);
        salir(i, { opacity: 0 }, t1, 0.2);
        break;
      case "sello":
        ver(s, t0, t1);
        desde(i, { opacity: 0, scale: 1.9, rotation: 16 }, { opacity: 1, scale: 1, rotation: 6 }, t0, 0.3, "back.out(1.6)");
        salir(i, { opacity: 0, scale: 0.9 }, t1, 0.2);
        break;
      case "dato":
        ver(s, t0, t1);
        desde(i, { opacity: 0, y: 60 }, { opacity: 1, y: 0 }, t0, M.entra, M.rebote);
        desde(s + " .eti", { opacity: 0 }, { opacity: 1 }, t0 + 0.2, 0.3);
        desde(s + " .fu", { opacity: 0 }, { opacity: 0.8 }, t0 + 0.35, 0.3);
        salir(i, { opacity: 0, y: -20 }, t1);
        break;
      case "cierre":
        ver(s, t0, t1);
        desde(i, { opacity: 0, scale: 0.7, rotation: -4 }, { opacity: 1, scale: 1, rotation: -2 }, t0, 0.4, "back.out(1.5)");
        // la flecha baja y sube dos veces: empuja la mirada a los comentarios
        tl.to(s + " .flecha", { y: 16, duration: 0.35, ease: "sine.inOut", yoyo: true, repeat: 3 }, t0 + 0.45);
        break;
      case "foto":
        ver(s, t0, t1);
        if (p.modo === "tarjeta") {
          desde(i, { opacity: 0, y: 80, rotation: -3, scale: 0.94 }, { opacity: 1, y: 0, rotation: -1.2, scale: 1 }, t0, M.entra, M.rebote);
          salir(i, { opacity: 0, y: 50 }, t1);
        } else {
          desde(i, { opacity: 0 }, { opacity: 1 }, t0, 0.12, "none");
          desde(s + " img", { scale: 1.0 }, { scale: 1.07 }, t0, dur, "none");
          salir(i, { opacity: 0 }, t1, 0.12);
        }
        break;
      case "inserto":
        ver(s, t0, t1);
        desde(i, { clipPath: "circle(0% at 50% 50%)" }, { clipPath: "circle(86% at 50% 50%)" }, t0, 0.38, "power3.inOut");
        tl.to(i, { clipPath: "circle(0% at 50% 50%)", duration: 0.3, ease: "power3.in" }, Math.max(t0 + 0.4, t1 - 0.3));
        break;
      case "sticker":
        ver(s, t0, t1);
        desde(i, { opacity: 0, scale: 0.5, rotation: -8 }, { opacity: 1, scale: 1, rotation: 0 }, t0, 0.38, "back.out(1.6)");
        salir(i, { opacity: 0, scale: 0.8 }, t1);
        break;
      case "detras":
        ver(s, t0, t1);
        desde(i, { opacity: 0, scale: 0.6, y: 60 }, { opacity: 1, scale: 1, y: 0 }, t0, 0.45, "back.out(1.4)");
        salir(i, { opacity: 0, y: 40 }, t1);
        break;
      case "barra":
        ver(s, t0, t1);
        desde(i, { scaleX: 0 }, { scaleX: 1 }, t0, dur, "none");
        break;
      case "barrido":
        ver(s, t0, t1);
        desde(i, { xPercent: -101 }, { xPercent: 0 }, t0, dur * 0.5, "power3.in");
        tl.to(i, { xPercent: 101, duration: dur * 0.5, ease: "power3.out" }, t0 + dur * 0.5);
        break;
      case "particulas":
        ver(s, t0, t1);
        var azar = semilla(p.id);
        for (var k = 0; k < p.n; k++) {
          // salen hacia los lados y caen: nunca suben hacia la cara
          var lado = azar() < 0.5 ? 1 : -1;
          var dist = W * (0.16 + 0.3 * azar());
          var q = s + "k" + k;
          desde(q, { x: 0, y: 0, opacity: 1, scale: 0.4, rotation: 0 },
            { x: lado * dist, y: H * (0.04 + 0.16 * azar()), opacity: 0, scale: 1, rotation: 360 * (azar() - 0.5) },
            t0 + 0.04 * azar(), Math.min(dur, 0.9 + 0.3 * azar()), "power2.out");
        }
        break;
      case "zoom":
        // acercamiento suave hacia la cara: entra con resorte corto, deriva lenta y regresa sin golpe
        var z = p.z, ox = foco[0] * (1 - z), oy = foco[1] * (1 - z);
        var entra = Math.min(0.5, dur * 0.35), sale = Math.min(0.45, dur * 0.3);
        if (p.modo === "push") {
          tl.to("#cam", { scale: z, x: ox, y: oy, duration: dur, ease: "sine.inOut" }, t0);
          tl.set("#cam", { scale: 1, x: 0, y: 0 }, t1);
        } else {
          tl.to("#cam", { scale: z, x: ox, y: oy, duration: entra, ease: "power3.out" }, t0);
          var z2 = z + 0.012;
          tl.to("#cam", { scale: z2, x: foco[0] * (1 - z2), y: foco[1] * (1 - z2), duration: Math.max(0.1, dur - entra - sale), ease: "none" }, t0 + entra);
          tl.to("#cam", { scale: 1, x: 0, y: 0, duration: sale, ease: "power2.inOut" }, t1 - sale);
        }
        break;
      case "panel":
        var c = p.cam, mv = 0.6;
        tl.to("#camwrap", { clipPath: c.recorte, duration: mv, ease: "power3.inOut" }, t0);
        tl.to("#cam", { scale: c.s, x: c.x, y: c.y, duration: mv, ease: "power3.inOut" }, t0);
        ver(s, t0 + 0.15, t1);
        desde(i, { opacity: 0, y: -50 }, { opacity: 1, y: 0 }, t0 + 0.2, 0.45, M.rebote);
        for (var n = 0; n < (p.items || 0); n++) {
          desde(s + "i" + n, { opacity: 0, x: -40 }, { opacity: 1, x: 0 }, t0 + 0.5 + n * Math.min(0.9, (dur - 1.4) / Math.max(1, p.items)), 0.35);
        }
        salir(i, { opacity: 0, y: -30 }, t1 - mv * 0.5);
        tl.to("#camwrap", { clipPath: "inset(0px 0px 0px 0px round 0px)", duration: mv, ease: "power3.inOut" }, t1 - mv);
        tl.to("#cam", { scale: 1, x: 0, y: 0, duration: mv, ease: "power3.inOut" }, t1 - mv);
        break;
    }
  });

  // ----- subtítulos: un grupo a la vez; entrada solo después de una pausa real -----
  var activo = getComputedStyle(document.documentElement).getPropertyValue("--acento").trim() || "#ffcc00";
  var previoEncadenado = false;
  P.grupos.forEach(function (g, k) {
    var s = "#g" + k;
    ver(s, g.t0, g.t1);
    if (!previoEncadenado) {
      desde(s, { scale: 0.92, opacity: 0 }, { scale: 1, opacity: 1 }, g.t0, 0.12, "power2.out");
    }
    previoEncadenado = g.enc;
    if (P.subs.modo === "karaoke") {
      g.w.forEach(function (w, n) {
        var q = s + "w" + n;
        tl.set(q, { color: activo, scale: 1.08 }, w[0]);
        tl.set(q, { color: P.subs.color, scale: 1 }, Math.max(w[1], w[0] + 0.08));
      });
    }
  });

  // la línea de tiempo dura exactamente el video
  tl.set({}, {}, P.duracion);
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
})();
