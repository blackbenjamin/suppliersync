"""
Pytest configuration for SupplierSync tests.
This file ensures the suppliersync modules can be imported.
"""

import sys
from pathlib import Path

# Add the suppliersync directory to Python path
suppliersync_dir = Path(__file__).parent.parent
sys.path.insert(0, str(suppliersync_dir))

