"""A person's yes, asked on this PC's screen (not through Claude), before any order on a LIVE account.
An assistant can be talked into calling place_order (by text in a web page, an email or another tool's output); it cannot
click this dialog. Windows only; anywhere else the answer is no, so live orders cannot go out unattended."""
import sys, time
MAX_WAIT_S = 60          # an answer given later than this is refused: the price has moved, preview again
def _dialog(title, text):
    import ctypes
    MB_YESNO, MB_ICONWARNING, MB_DEFBUTTON2, MB_SYSTEMMODAL, MB_SETFOREGROUND, MB_TOPMOST = 0x4, 0x30, 0x100, 0x1000, 0x10000, 0x40000
    return ctypes.windll.user32.MessageBoxW(None, text, title, MB_YESNO | MB_ICONWARNING | MB_DEFBUTTON2 | MB_SYSTEMMODAL | MB_SETFOREGROUND | MB_TOPMOST) == 6
def confirm(title, text, dialog=None):
    """True only if the person clicked Yes within MAX_WAIT_S seconds."""
    if dialog is None:
        if sys.platform != 'win32': return False
        dialog = _dialog
    t0 = time.monotonic(); yes = bool(dialog(title, text))
    return yes and time.monotonic() - t0 <= MAX_WAIT_S
