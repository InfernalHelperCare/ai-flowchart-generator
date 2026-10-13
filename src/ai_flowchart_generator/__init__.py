"""ai-flowchart-generator: AI-driven flowchart generation toolkit.

Public surface is intentionally small. Import from subpackages for
anything deeper than the pipeline entry point.
"""

from ai_flowchart_generator.pipeline import FlowchartPipeline, PipelineResult

__all__ = ["FlowchartPipeline", "PipelineResult", "__version__"]

__version__ = "0.6.3"