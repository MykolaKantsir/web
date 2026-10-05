"""
Short-lived in-memory relay for drawings of queued jobs (long time plan).

Django runs in the cloud and cannot read the drawing PDFs; only the on-prem
Monitor watcher can. So the tablet files a request here, the watcher picks it up,
renders the drawing and pushes it back, and the tablet fetches it.

Nothing is persisted: images live in process RAM only, expire after TTL_SECONDS
and the cache holds at most MAX_IMAGES (oldest dropped first), so memory stays
bounded no matter how many machines there are. A restart empties it.
"""
import threading
import time
from collections import OrderedDict

TTL_SECONDS = 10 * 60        # an image is forgotten this long after it arrived
MAX_IMAGES = 20              # hard cap on cached images (LRU by arrival)
REQUEST_TTL_SECONDS = 120    # an unanswered request is dropped after this long
WORKING_RETRY_SECONDS = 60   # hand a request to the watcher again if it was claimed but never answered

_lock = threading.Lock()
_images = OrderedDict()      # operation id -> (arrived_at, data_url or '' for "no drawing")
_requests = {}               # operation id -> {'part_id', 'name', 'requested_at', 'claimed_at'}


def _purge_images(now):
    for key in [k for k, (t, _) in _images.items() if now - t > TTL_SECONDS]:
        del _images[key]
    while len(_images) > MAX_IMAGES:
        _images.popitem(last=False)


def _purge_requests(now):
    for key in [k for k, r in _requests.items() if now - r['requested_at'] > REQUEST_TTL_SECONDS]:
        del _requests[key]


def put_image(op_id, data_url):
    """Store a rendered drawing ('' means the part has no drawing) and close its request."""
    now = time.time()
    with _lock:
        _images.pop(op_id, None)
        _images[op_id] = (now, data_url or '')
        _requests.pop(op_id, None)
        _purge_images(now)


def get_image(op_id):
    """Return (found, data_url). Expired entries are deleted and count as not found."""
    now = time.time()
    with _lock:
        _purge_images(now)
        entry = _images.get(op_id)
        if entry is None:
            return False, None
        return True, entry[1]


def request_image(op_id, part_id='', name=''):
    """Register that a tablet wants this drawing (no-op if already cached or requested)."""
    now = time.time()
    with _lock:
        _purge_images(now)
        _purge_requests(now)
        if op_id in _images or op_id in _requests:
            return
        _requests[op_id] = {'part_id': part_id, 'name': name, 'requested_at': now, 'claimed_at': None}


def claim_pending():
    """Requests for the watcher to fulfil; marks them claimed so they aren't handed out every poll."""
    now = time.time()
    with _lock:
        _purge_requests(now)
        out = []
        for op_id, r in _requests.items():
            if r['claimed_at'] is None or now - r['claimed_at'] > WORKING_RETRY_SECONDS:
                r['claimed_at'] = now
                out.append({'monitor_operation_id': op_id, 'part_id': r['part_id'], 'name': r['name']})
        return out
