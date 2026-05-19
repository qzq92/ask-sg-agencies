"""Windows SSL workaround for OPENSSL_Applink errors.

On Windows, antivirus or network monitoring tools may set SSLKEYLOGFILE
(e.g. NetLimiter / nllMonFltProxy). That triggers:

    OPENSSL_Uplink(...): no OPENSSL_Applink

when urllib3/requests initialize SSL. Remove it before any HTTPS imports.
"""

import os
import sys


def apply_windows_ssl_fix() -> None:
    """Unset SSLKEYLOGFILE on Windows if present."""
    if sys.platform != "win32":
        return
    if os.environ.get("SSLKEYLOGFILE"):
        os.environ.pop("SSLKEYLOGFILE", None)
