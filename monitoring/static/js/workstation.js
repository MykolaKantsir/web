// Workstation screen: polls JSON and updates the DOM in place (no page reload).
// Slides: info -> drawing -> long time plan.
// Drag right-to-left / ArrowRight = next slide, drag left-to-right / ArrowLeft = previous.
(function () {
  var POLL_MS = 120 * 1000;  // matches the Monitor G5 update_watcher loop
  var SLIDE_COUNT = 3;
  var body = document.body;
  var apiUrl = body.dataset.apiUrl;
  var drawingUrlTemplate = body.dataset.drawingUrl;  // .../api/drawing/0/
  var last = null;
  var slideIndex = 0;
  var drawingKey = null;  // "<operation pk>:<article>" of the drawing currently shown

  var el = {
    slides: document.getElementById('slides'),
    article: document.getElementById('article'),
    users: document.getElementById('users'),
    numbers: document.getElementById('numbers'),
    made: document.getElementById('made'),
    required: document.getElementById('required'),
    next: document.getElementById('next'),
    drawing: document.getElementById('drawing-image'),
    noDrawing: document.getElementById('no-drawing'),
    queue: document.getElementById('queue'),
    overlay: document.getElementById('overlay'),
    overlayImage: document.getElementById('overlay-image'),
    overlayMsg: document.getElementById('overlay-msg'),
    overlayBack: document.getElementById('overlay-back')
  };
  var drawingRequestUrl = body.dataset.drawingRequestUrl;
  var queueDrawingUrl = body.dataset.queueDrawingUrl;  // .../api/queue-drawing/OPID/
  var queueItems = [];
  var overlayToken = 0;  // bumped on every open/close so stale polls stop themselves
  var QUEUE_POLL_MS = 2000;
  var QUEUE_GIVE_UP_MS = 30 * 1000;

  // ---- Slides ----
  function showSlide(i) {
    slideIndex = (i + SLIDE_COUNT) % SLIDE_COUNT;
    el.slides.style.transform = 'translateX(-' + (slideIndex * 100 / SLIDE_COUNT) + '%)';
  }
  var fromUrl = parseInt(new URLSearchParams(location.search).get('slide'), 10);
  if (!isNaN(fromUrl)) showSlide(fromUrl);

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

  // ---- Drawing ----
  function showDrawing(src) {
    if (src) {
      el.drawing.src = src;
      el.drawing.style.display = 'block';
      el.noDrawing.style.display = 'none';
    } else {
      el.drawing.removeAttribute('src');
      el.drawing.style.display = 'none';
      el.noDrawing.style.display = 'block';
    }
  }

  // Fetch the drawing only when the operation (or its name, since monitor
  // operations are rewritten in place) changed; drawings are large base64 blobs.
  function updateDrawing(d) {
    var key = d.operation_id ? d.operation_id + ':' + d.article : '';
    if (key === drawingKey) return;
    drawingKey = key;
    if (!d.operation_id) { showDrawing(''); return; }
    fetch(drawingUrlTemplate.replace(/0\/$/, d.operation_id + '/'), { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (j) { if (drawingKey === key) showDrawing(j.drawing_base64); })
      .catch(function () { drawingKey = null; });  // retry on next poll
  }

  // ---- Long time plan (queue) ----
  function renderQueue(items) {
    queueItems = items || [];
    el.queue.innerHTML = '';
    if (!queueItems.length) {
      var empty = document.createElement('div');
      empty.className = 'q-empty';
      empty.textContent = 'NOT PLANNED';
      el.queue.appendChild(empty);
      return;
    }
    queueItems.forEach(function (item, i) {
      var row = document.createElement('div');
      row.className = 'q-row';
      row.dataset.index = i;
      var art = document.createElement('div');
      art.className = 'q-article';
      var span = document.createElement('span');
      span.textContent = item.article;
      art.appendChild(span);
      var qty = document.createElement('div');
      qty.className = 'q-qty';
      qty.textContent = item.quantity;
      row.appendChild(art);
      row.appendChild(qty);
      el.queue.appendChild(row);
      fit(span, 40);
    });
  }

  // ---- Drawing viewer (tap a queue row) ----
  function overlayMessage(text) {
    el.overlayImage.style.display = 'none';
    el.overlayMsg.textContent = text;
    el.overlayMsg.style.display = 'block';
  }
  function overlayShow(src) {
    if (!src) { overlayMessage('No drawing available'); return; }
    el.overlayMsg.style.display = 'none';
    el.overlayImage.src = src;
    el.overlayImage.style.display = 'block';
  }
  function closeOverlay() {
    overlayToken++;
    el.overlay.classList.remove('open');
    el.overlayImage.removeAttribute('src');
  }
  function isOverlayOpen() { return el.overlay.classList.contains('open'); }

  function openDrawing(item) {
    var token = ++overlayToken;
    el.overlay.classList.add('open');
    overlayMessage('Loading…');

    // Already stored (the machine's next job): same endpoint as the drawing slide
    if (item.drawing_pk) {
      fetch(drawingUrlTemplate.replace(/0\/$/, item.drawing_pk + '/'), { cache: 'no-store' })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (j) { if (token === overlayToken) overlayShow(j.drawing_base64); })
        .catch(function () { if (token === overlayToken) overlayMessage('Drawing not available right now'); });
      return;
    }

    // Otherwise ask the watcher (via Django) to render it, then poll until it arrives
    var deadline = Date.now() + QUEUE_GIVE_UP_MS;
    function poll() {
      if (token !== overlayToken) return;
      fetch(queueDrawingUrl.replace('OPID', encodeURIComponent(item.monitor_operation_id)), { cache: 'no-store' })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (j) {
          if (token !== overlayToken) return;
          if (j.status === 'ready') overlayShow(j.drawing_base64);
          else if (j.status === 'none') overlayMessage('No drawing available');
          else if (Date.now() > deadline) overlayMessage('Drawing not available right now');
          else setTimeout(poll, QUEUE_POLL_MS);
        })
        .catch(function () { if (token === overlayToken) overlayMessage('Drawing not available right now'); });
    }
    fetch(drawingRequestUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ machine_id: parseInt(body.dataset.machineId, 10), monitor_operation_id: item.monitor_operation_id })
    })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function () { poll(); })
      .catch(function () { if (token === overlayToken) overlayMessage('Drawing not available right now'); });
  }

  el.queue.addEventListener('click', function (e) {
    var row = e.target.closest('.q-row');
    if (row) openDrawing(queueItems[parseInt(row.dataset.index, 10)]);
  });
  el.overlayBack.addEventListener('click', closeOverlay);

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
    body.style.setProperty('--p', pct + '%');
    el.next.textContent = d.next_article || 'NOT PLANNED';
    fit(el.made, 120);
    fit(el.required, 120);
    fit(el.article, 70);
    fit(el.next, 20);
    updateDrawing(d);
    renderQueue(d.queue);
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

  // Swipe (touch) between slides
  var touchStart = null;
  document.addEventListener('touchstart', function (e) {
    var t = e.changedTouches[0];
    touchStart = { x: t.clientX, y: t.clientY };
  }, { passive: true });
  document.addEventListener('touchend', function (e) {
    if (!touchStart || isOverlayOpen()) { touchStart = null; return; }  // no swiping while a drawing is open
    var t = e.changedTouches[0];
    var dx = t.clientX - touchStart.x, dy = t.clientY - touchStart.y;
    touchStart = null;
    // Drag right-to-left (dx < 0) = next slide, like the strip itself moves
    if (Math.abs(dx) > 80 && Math.abs(dx) > Math.abs(dy) * 1.5) showSlide(slideIndex + (dx < 0 ? 1 : -1));
  }, { passive: true });
  document.addEventListener('keydown', function (e) {
    if (isOverlayOpen()) { if (e.key === 'Escape') closeOverlay(); return; }
    if (e.key === 'ArrowRight') showSlide(slideIndex + 1);
    else if (e.key === 'ArrowLeft') showSlide(slideIndex - 1);
  });

  poll();
  setInterval(poll, POLL_MS);
  // Re-fit once fonts are ready and when the viewport changes (rotation, Chrome fullscreen)
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
  window.addEventListener('resize', refit);
})();
