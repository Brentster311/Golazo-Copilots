"""Tkinter desktop app for SFI Reporter.

Backward-compatible re-export shim.  All public names that were
originally defined in this single-file module are now split across:

    sfi_reporter.models      -- data types, constants, column utilities
    sfi_reporter.formatters  -- text formatting, URL extraction
    sfi_reporter.services    -- business logic, data refresh, filters
    sfi_reporter.dialogs     -- Tkinter dialogs & widgets
    sfi_reporter.app         -- SFIReporterApp class & main()

Existing `from sfi_reporter.tk_app import X` statements continue to
work because this module star-imports every public name.
"""

# ruff: noqa: F401 F403  intentional re-exports
from sfi_reporter.models import *       # noqa: F401,F403
from sfi_reporter.formatters import *   # noqa: F401,F403
from sfi_reporter.services import *     # noqa: F401,F403
from sfi_reporter.dialogs import *      # noqa: F401,F403
from sfi_reporter.app import *          # noqa: F401,F403

if __name__ == "__main__":
    main()
