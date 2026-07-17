"""Re-export clinical synthetic data generator for ML pipeline."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.generators.synthetic_clinical import generate_gene_therapy_data  # noqa: E402

__all__ = ["generate_gene_therapy_data"]
