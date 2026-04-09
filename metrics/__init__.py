"""Metrics module for the Genesis Creativity Engine.

Provides the Go Essence scoring framework for evaluating generated games
across multiple quality dimensions: rule simplicity, strategic depth,
non-triviality, and strategic diversity.
"""

from metrics.scoring import GoEssenceScorer

__all__ = ["GoEssenceScorer"]
