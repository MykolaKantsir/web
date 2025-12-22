import threading
from datetime import datetime

# In-memory cursor state (thread-safe)
_cursor_state = {
    'operation_id': None,
    'last_activity': None,
    'is_active': False
}
_cursor_lock = threading.Lock()

# Configuration
CURSOR_TIMEOUT_SECONDS = 180  # 3 minutes

def set_cursor(operation_id):
    """
    Update cursor position and mark as active.
    Returns the cursor state.
    """
    with _cursor_lock:
        _cursor_state['operation_id'] = operation_id
        _cursor_state['last_activity'] = datetime.now()
        _cursor_state['is_active'] = True
        return _cursor_state.copy()

def get_active_cursor():
    """
    Get current cursor state, checking if still active.
    Auto-deactivates if timeout exceeded.
    """
    with _cursor_lock:
        elapsed = None
        if _cursor_state['last_activity']:
            elapsed = (datetime.now() - _cursor_state['last_activity']).total_seconds()

            if elapsed > CURSOR_TIMEOUT_SECONDS:
                _cursor_state['is_active'] = False

        return {
            'operation_id': _cursor_state['operation_id'],
            'is_active': _cursor_state['is_active'],
            'last_activity': _cursor_state['last_activity'].isoformat() if _cursor_state['last_activity'] else None,
            'seconds_since_activity': elapsed if _cursor_state['last_activity'] else None
        }

def deactivate_cursor():
    """Manually deactivate cursor (e.g., on ESC key)."""
    with _cursor_lock:
        _cursor_state['is_active'] = False
        return _cursor_state.copy()
