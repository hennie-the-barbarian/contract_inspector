from fastapi.testclient import TestClient
from unittest.mock import patch
import io
import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import contract_red_flags.tasks.file_tasks as file_tasks
