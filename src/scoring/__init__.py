"""Metric aggregation + the three headline analyses (design.md §6).

`summarize(results_jsonl)` reads the run driver's output and returns Targeted ASR / Utility Under
Attack / PNA / NRP per cell, plus encoding lift, the surface-form-vs-behavioral defense-class split,
and the capability-scaling trend.
"""

from src.scoring.aggregate import (
    capability_scaling,
    cell_metrics,
    defense_class_split,
    encoding_lift,
    summarize,
)

__all__ = [
    "summarize",
    "cell_metrics",
    "encoding_lift",
    "defense_class_split",
    "capability_scaling",
]
