// Workstation screen: polls JSON and updates the DOM in place (no page reload).
// Themes: swipe right / ArrowRight = next theme, swipe left / ArrowLeft = previous.
// ?theme=<name> picks one explicitly; the choice is remembered per tablet.
(function () {
  var POLL_MS = 120 * 1000;  // matches the Monitor G5 update_watcher loop
  var THEMES = ['flat', 'minimal'];
  var body = document.body;
  var apiUrl = body.dataset.apiUrl;
  var last = null;

  var el = {
    article: document.getElementById('article'),
    users: document.getElementById('users'),
    numbers: document.getElementById('numbers'),
    made: document.getElementById('made'),
    required: document.getElementById('required'),
    next: document.getElementById('next')
  };

  // ---- Themes ----
  function storedTheme() {
    try { return localStorage.getItem('workstationTheme'); } catch (e) { return null; }
  }
  function setTheme(name) {
    if (THEMES.indexOf(name) === -1) name = THEMES[0];
    body.dataset.theme = name;
    try { localStorage.setItem('workstationTheme', name); } catch (e) {}
    // Clear sizes set by the other theme's fitting, then re-fit
    [el.made, el.required, el.article, el.next].forEach(function (n) { n.style.fontSize = ''; });
    el.numbers.style.removeProperty('--num-size');
    refit();
  }
  function stepTheme(delta) {
    var i = THEMES.indexOf(body.dataset.theme);
    setTheme(THEMES[(i + delta + THEMES.length) % THEMES.length]);
  }

  // ---- Fitting ----
  // Shrink text until it fits its container (long article names, big quantities).
  function fit(node, minPx) {
    var box = node.parentElement;
    var cs = getComputedStyle(box);
    // Usable width = content box of the parent (clientWidth includes padding)
    var avail = box.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 8;
    node.style.fontSize = '';
    var size = parseFloat(getComputedStyle(node).fontSize);
    while (node.getBoundingClientRect().width > avail && size > minPx) {
      size = Math.max(minPx, size - 4);
      node.style.fontSize = size + 'px';
    }
  }

  // Minimal theme: made / required share one line, sized together via --num-size.
  function fitNumbers() {
    var cs = getComputedStyle(el.numbers);
    var avail = el.numbers.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 8;
    var size = Math.max(120, Math.min(560, Math.floor(el.numbers.clientHeight * 0.95)));  // also fit the row height
    function rowWidth() {
      var w = 0;
      Array.prototype.forEach.call(el.numbers.children, function (c) { w += c.getBoundingClientRect().width; });
      return w;
    }
    el.numbers.style.setProperty('--num-size', size + 'px');
    while (rowWidth() > avail && size > 120) {
      size -= 10;
      el.numbers.style.setProperty('--num-size', size + 'px');
    }
  }

  function render(d) {
    last = d;
    body.classList.remove('state-running', 'state-setup', 'state-idle');
    body.classList.add('state-' + d.state);
    el.article.textContent = d.article || 'NOT STARTED';
    el.users.innerHTML = '';
    (d.users || []).forEach(function (name) {
      var div = document.createElement('div');
      div.className = 'user';
      div.textContent = name;
      el.users.appendChild(div);
    });
    el.made.textContent = d.made === null ? '—' : d.made;
    el.required.textContent = d.required === null ? '—' : d.required;
    var pct = d.article ? Math.max(0, Math.min(100, d.progress_percent)) : 0;
    body.style.setProperty('--p', pct + '%');  // read by every theme's progress gradient
    el.next.textContent = d.next_article || 'NOT PLANNED';

    if (body.dataset.theme === 'minimal') {
      fitNumbers();
    } else {
      fit(el.made, 120);
      fit(el.required, 120);
      fit(el.article, 70);
    }
    fit(el.next, 20);
  }

  function refit() { if (last) render(last); }

  function poll() {
    fetch(apiUrl, { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) { body.classList.remove('stale'); render(d); })
      .catch(function () { body.classList.add('stale'); });
  }

  // Tap the numbers row to toggle fullscreen (needs a user gesture; hides Chrome's bars)
  el.numbers.addEventListener('click', function () {
    var root = document.documentElement;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (root.requestFullscreen) {
      root.requestFullscreen().catch(function () {});
    }
  });
  document.addEventListener('fullscreenchange', function () { setTimeout(refit, 100); });

  // Swipe right = next theme, swipe left = previous
  var touchStart = null;
  document.addEventListener('touchstart', function (e) {
    var t = e.changedTouches[0];
    touchStart = { x: t.clientX, y: t.clientY };
  }, { passive: true });
  document.addEventListener('touchend', function (e) {
    if (!touchStart) return;
    var t = e.changedTouches[0];
    var dx = t.clientX - touchStart.x, dy = t.clientY - touchStart.y;
    touchStart = null;
    if (Math.abs(dx) > 80 && Math.abs(dx) > Math.abs(dy) * 1.5) stepTheme(dx > 0 ? 1 : -1);
  }, { passive: true });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') stepTheme(1);
    else if (e.key === 'ArrowLeft') stepTheme(-1);
  });

  var fromUrl = new URLSearchParams(location.search).get('theme');
  body.dataset.theme = THEMES.indexOf(fromUrl) !== -1 ? fromUrl :
                       THEMES.indexOf(storedTheme()) !== -1 ? storedTheme() : THEMES[0];

  poll();
  setInterval(poll, POLL_MS);
  // Re-fit once fonts are ready and when the viewport changes (rotation, Chrome fullscreen)
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
  window.addEventListener('resize', refit);
})();
