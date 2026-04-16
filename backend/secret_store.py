import base64
import ctypes
import os
from ctypes import wintypes


_DPAPI_PREFIX = "dpapi:"
_PLAIN_PREFIX = "plain:"


class _DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _blob_from_bytes(data: bytes) -> _DATA_BLOB:
    buf = ctypes.create_string_buffer(data)
    return _DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))


def _blob_to_bytes(blob: _DATA_BLOB) -> bytes:
    if not blob.cbData:
        return b""
    return ctypes.string_at(blob.pbData, blob.cbData)


def _dpapi_protect(raw: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    in_blob = _blob_from_bytes(raw)
    out_blob = _DATA_BLOB()
    ok = crypt32.CryptProtectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    )
    if not ok:
        raise ctypes.WinError()
    try:
        return _blob_to_bytes(out_blob)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def _dpapi_unprotect(encrypted: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    in_blob = _blob_from_bytes(encrypted)
    out_blob = _DATA_BLOB()
    ok = crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    )
    if not ok:
        raise ctypes.WinError()
    try:
        return _blob_to_bytes(out_blob)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def protect_text(value: str) -> str:
    text = value or ""
    raw = text.encode("utf-8")
    if os.name == "nt":
        encrypted = _dpapi_protect(raw)
        return _DPAPI_PREFIX + base64.b64encode(encrypted).decode("ascii")
    return _PLAIN_PREFIX + base64.b64encode(raw).decode("ascii")


def unprotect_text(stored: str) -> str:
    value = stored or ""
    if value.startswith(_DPAPI_PREFIX):
        encrypted = base64.b64decode(value[len(_DPAPI_PREFIX) :])
        decrypted = _dpapi_unprotect(encrypted)
        return decrypted.decode("utf-8", errors="ignore")
    if value.startswith(_PLAIN_PREFIX):
        raw = base64.b64decode(value[len(_PLAIN_PREFIX) :])
        return raw.decode("utf-8", errors="ignore")
    return value

