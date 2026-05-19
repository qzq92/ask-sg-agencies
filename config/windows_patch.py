"""Windows SSL workarounds.

Fixes two common issues on Windows:

1. OPENSSL_Applink error: Network monitoring tools (e.g. NetLimiter) set
   SSLKEYLOGFILE which causes "OPENSSL_Uplink(...): no OPENSSL_Applink"
   when urllib3/requests initialize SSL.

2. SSL certificate verification failure: Corporate proxies or firewalls
   doing SSL inspection use certificates not in Python's default store.
   Using truststore injects Windows' native certificate store.

Import and call apply_windows_ssl_fix() at the very top of your entrypoint,
before any other imports that may trigger HTTPS connections.
"""

import os
import sys


def apply_windows_patch() -> None:
    """Apply Windows patches. Call before any HTTPS-related imports."""
    if sys.platform != "win32":
        return

    # Fix OPENSSL_Applink error from network monitoring tools
    os.environ.pop("SSLKEYLOGFILE", None)

    # Use Windows native certificate store (trusts corporate proxy certs)
    try:
        import truststore
        truststore.inject_into_ssl()
    except ImportError:
        pass
