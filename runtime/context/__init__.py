"""Runtime execution-context adapters."""

from runtime.context.inbound import InboundContextBuilder, InboundContextSpec
from runtime.context.propagation import ContextPropagator, PropagationOverrides
from runtime.context.snapshot import ContextSnapshot

__all__ = [
    "ContextPropagator",
    "ContextSnapshot",
    "InboundContextBuilder",
    "InboundContextSpec",
    "PropagationOverrides",
]
