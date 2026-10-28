/* Shared timeline builders for the v2 trailer (v2/trailer60) and cutdown (v2/cutdown30).
   Linked into each project as assets/filmkit.js. Every function only adds tweens/sets to the
   paused root timeline at absolute times: the picture is a pure function of timeline time.
   Footage coordinates ("frame px") are pixels of the source frame scaled to 1920x1080: the 4K
   clip's terminal grid spans x 112..1808, rows of 32.5 px from y 20 (row r centre 36.25 + 32.5 r). */
(function () {
  var K = {};
  var NS = "http://www.w3.org/2000/svg";
  var EXPO = "expo.out";       // enter, cubic-bezier(0.16, 1, 0.3, 1)
  var CAM = "power3.inOut";    // camera moves

  function q(sel, root) { return (root || document).querySelector(sel); }
  K.q = q;

  // ---------------------------------------------------------------- text helpers
  // Split an element's text into per-character spans. Tokens wrapped in [..] in `src` are cyan.
  // Returns the char spans (spaces included, so indices match the typed string).
  K.chars = function (el, src, cls) {
    el.textContent = "";
    var out = [], cyan = false;
    for (var i = 0; i < src.length; i++) {
      var ch = src[i];
      if (ch === "[") { cyan = true; continue; }
      if (ch === "]") { cyan = false; continue; }
      var s = document.createElement("span");
      s.className = "ch" + (cyan ? " c" : "") + (cls ? " " + cls : "");
      s.textContent = ch;
      el.appendChild(s);
      out.push(s);
    }
    return out;
  };
  // Reveal spans at the given times (one per span), one set per span.
  K.typeOn = function (tl, spans, times) {
    // 2 ms early so float rounding can never push a character one frame late
    spans.forEach(function (s, i) { tl.set(s, { visibility: "visible" }, Math.max(0, times[i] - 0.002)); });
  };
  // Times for a type-on at `perChar` seconds, snapped up to the frame grid.
  K.times = function (n, t0, perChar) {
    var out = [];
    for (var i = 0; i < n; i++) out.push(Math.ceil((t0 + i * perChar) * 30 - 1e-6) / 30);
    return out;
  };
  // Block cursor that follows a typed line: x = n characters (monospace 0.6 em).
  K.cursorFollow = function (tl, cur, times, emPx, startN) {
    var base = startN || 0;
    gsap.set(cur, { x: base * 0.6 * emPx });
    times.forEach(function (t, i) { tl.set(cur, { x: (base + i + 1) * 0.6 * emPx }, Math.max(0, t - 0.002)); });
  };
  // Beat-locked blink: on for 0.5 s, off for 0.5 s, from t0 to t1 (on at t0), then left `endState`.
  K.blink = function (tl, el, t0, t1, endOn) {
    for (var t = t0; t < t1 - 1e-6; t += 1.0) {
      tl.set(el, { opacity: 1 }, t);
      if (t + 0.5 < t1 - 1e-6) tl.set(el, { opacity: 0 }, t + 0.5);
    }
    tl.set(el, { opacity: endOn === false ? 0 : 1 }, t1);
  };

  // ---------------------------------------------------------------- owl glyph (brand/owl.txt)
  // Quadrant blocks drawn as rects (the brand fonts have no block glyphs). Eyes (row 1, the two
  // ▟▙ pairs) are returned as a separate group so they can light up.
  var QUAD = { "▀": [1, 1, 0, 0], "▄": [0, 0, 1, 1], "▌": [1, 0, 1, 0], "▐": [0, 1, 0, 1],
    "▙": [1, 0, 1, 1], "▛": [1, 1, 1, 0], "▜": [1, 1, 0, 1], "▟": [0, 1, 1, 1] };
  K.owl = function (svg, rows, cellW, cellH) {
    svg.setAttribute("width", rows[0].length * cellW);
    svg.setAttribute("height", rows.length * cellH);
    svg.setAttribute("viewBox", "0 0 " + rows[0].length * cellW + " " + rows.length * cellH);
    svg.setAttribute("shape-rendering", "crispEdges");
    var body = document.createElementNS(NS, "g"), eyes = document.createElementNS(NS, "g");
    body.setAttribute("fill", "#FAFAFA");
    rows.forEach(function (row, r) {
      Array.prototype.forEach.call(row, function (ch, c) {
        var qd = QUAD[ch];
        if (!qd) return;
        var isEye = r === 1 && c > 0 && c < row.length - 1;
        var hw = cellW / 2, hh = cellH / 2;
        [[0, 0], [1, 0], [0, 1], [1, 1]].forEach(function (p, k) {
          if (!qd[k]) return;
          var rc = document.createElementNS(NS, "rect");
          rc.setAttribute("x", c * cellW + p[0] * hw);
          rc.setAttribute("y", r * cellH + p[1] * hh);
          rc.setAttribute("width", hw + 0.5);
          rc.setAttribute("height", hh + 0.5);
          (isEye ? eyes : body).appendChild(rc);
        });
      });
    });
    svg.appendChild(body);
    svg.appendChild(eyes);
    return { body: body, eyes: eyes };
  };

  // ---------------------------------------------------------------- camera over the footage
  // A rect is {z, cx, cy}: zoom and the frame-px point at the screen centre (clamped in frame).
  K.camVars = function (r) {
    var z = r.z;
    var cx = Math.min(Math.max(r.cx, 960 / z), 1920 - 960 / z);
    var cy = Math.min(Math.max(r.cy, 540 / z), 1080 - 540 / z);
    return { x: 960 - cx * z, y: 540 - cy * z, scale: z / 2 };   // the <video> is 3840x2160
  };
  K.clampRect = function (r) {
    var v = K.camVars(r);
    return { z: r.z, cx: (960 - v.x) / r.z, cy: (540 - v.y) / r.z };
  };
  // Zoom rect r by k keeping frame point (ax, ay) fixed on screen (slow drift).
  K.drift = function (r, k, ax, ay) {
    var c = K.clampRect(r), z2 = c.z * k;
    var sx = (ax - c.cx) * c.z, sy = (ay - c.cy) * c.z;
    return { z: z2, cx: ax - sx / z2, cy: ay - sy / z2 };
  };
  K.toScreen = function (box, r) {   // frame-px box [x0,y0,x1,y1] -> screen box
    var v = K.camVars(r), s = v.scale * 2;
    return [v.x + box[0] * s, v.y + box[1] * s, v.x + box[2] * s, v.y + box[3] * s];
  };
  K.camSet = function (tl, cam, t, r) { tl.set(cam, K.camVars(r), t); };
  K.camTo = function (tl, cam, t, d, r, ease) {
    var v = K.camVars(r); v.duration = d; v.ease = ease || CAM; v.immediateRender = false;
    tl.to(cam, v, t);
  };

  // Focus brackets: snap around a frame-px box at t0, follow the camera's linear drift to t1
  // (rect r0 -> r1), hide at tOff. pad = screen px around the box.
  K.brackets = function (tl, el, box, t0, r0, t1, r1, tOff, pad) {
    pad = pad == null ? 12 : pad;
    function geo(r) {
      var s = K.toScreen(box, r);
      return { x: s[0] - pad, y: s[1] - pad, width: s[2] - s[0] + 2 * pad, height: s[3] - s[1] + 2 * pad };
    }
    var g0 = geo(r0), g1 = geo(r1);
    tl.set(el, { x: g0.x, y: g0.y, width: g0.width, height: g0.height, visibility: "visible" }, t0);
    tl.fromTo(el, { opacity: 0, scale: 1.10 }, { opacity: 1, scale: 1, duration: 0.18, ease: EXPO, immediateRender: false }, t0);
    tl.to(el, { x: g1.x, y: g1.y, width: g1.width, height: g1.height, duration: Math.max(t1 - t0, 0.01), ease: "none", immediateRender: false }, t0);
    tl.to(el, { opacity: 0, duration: 0.2, ease: "power2.in", immediateRender: false }, tOff);
    tl.set(el, { visibility: "hidden" }, tOff + 0.2);
  };

  // Verb plate: 2-frame opacity snap, scale 1.12 -> 1.00 over 0.25 s, hard cut out.
  K.verb = function (tl, el, tIn, tOut) {
    tl.set(el, { visibility: "visible" }, tIn);
    tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 2 / 30, ease: "none", immediateRender: false }, tIn);
    tl.fromTo(el, { scale: 1.12 }, { scale: 1, duration: 0.25, ease: EXPO, immediateRender: false }, tIn);
    tl.set(el, { visibility: "hidden" }, tOut);
  };

  // Keycap: enters 0.35 s before the press, presses on tPress (cap dips, lights), spark fires.
  K.keycap = function (tl, el, tIn, tPress, tOut, hardOut) {
    var cap = q(".cap", el), spark = q(".spark", el), dia = q("polygon", spark);
    tl.set(el, { visibility: "visible" }, tIn);
    tl.fromTo(el, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.3, ease: EXPO, immediateRender: false }, tIn);
    tl.to(cap, { y: 5, duration: 0.05, ease: "power2.in", immediateRender: false }, tPress - 0.05);
    tl.set(cap, { borderColor: "#00F0FF", backgroundColor: "rgba(0,240,255,0.15)" }, tPress);
    tl.to(cap, { y: 0, duration: 0.18, ease: EXPO, immediateRender: false }, tPress);
    tl.to(cap, { borderColor: "#27272A", backgroundColor: "#18181B", duration: 0.35, ease: "power2.out", immediateRender: false }, tPress + 0.08);
    K.spark(tl, spark, tPress, 0.30);
    tl.set(spark, { visibility: "hidden" }, tOut);
    if (hardOut) tl.set(el, { visibility: "hidden" }, tOut);
    else {
      tl.to(el, { opacity: 0, duration: 0.2, ease: "power2.in", immediateRender: false }, tOut - 0.2);
      tl.set(el, { visibility: "hidden" }, tOut);
    }
  };
  // Spark: diamond scales 0 -> 1.18 -> 1.0 over d (back.out(2.2)), glow 0 -> 24 -> 8 px.
  K.spark = function (tl, el, t, d) {
    t = t - 1 / 30;   // one frame early: the diamond is already up on the event frame
    tl.set(el, { visibility: "visible", transformOrigin: "50% 50%" }, t);
    tl.fromTo(el, { scale: 0 }, { scale: 1, duration: d || 0.3, ease: "back.out(2.2)", immediateRender: false }, t);
    tl.fromTo(el, { filter: "drop-shadow(0 0 0px rgba(0,240,255,0.40))" },
      { filter: "drop-shadow(0 0 16px rgba(0,240,255,0.45))", duration: 0.12, ease: "power2.out", immediateRender: false }, t);
    tl.to(el, { filter: "drop-shadow(0 0 8px rgba(0,240,255,0.40))", duration: 0.3, ease: "power2.out", immediateRender: false }, t + 0.12);
  };

  // Stroke draw for SVG shapes (stroke-dashoffset).
  K.draw = function (tl, els, t, d, ease) {
    [].concat(els).forEach(function (el) {
      var L = el.getTotalLength ? el.getTotalLength() : 100;
      gsap.set(el, { strokeDasharray: L + " " + L, strokeDashoffset: L, visibility: "hidden" });
      tl.set(el, { visibility: "visible" }, t);   // hidden until it draws (a round cap would show a dot)
      tl.to(el, { strokeDashoffset: 0, duration: d, ease: ease || "power2.inOut", immediateRender: false }, t);
    });
  };

  // Rise-in (enter): opacity 0 -> 1, y +dy -> 0, expo.out 0.45 s.
  K.rise = function (tl, el, t, dy, d) {
    tl.set(el, { visibility: "visible" }, t);
    tl.fromTo(el, { opacity: 0, y: dy == null ? 24 : dy }, { opacity: 1, y: 0, duration: d || 0.45, ease: EXPO, immediateRender: false }, t);
  };

  window.FilmKit = K;
})();
