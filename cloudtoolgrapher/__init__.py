import importlib.metadata


# get version from pyproject.toml
__version__ = importlib.metadata.version(__package__ or __name__)

# get the underlying classes in the namespace
from .awsinfo import AWSInfo
from .grapher import graph
from .jobruns import JobRuns
from .plots import DeltaPlot, ToolPlot
from .toolresources import ToolResourceRequests
from .toolrundata import ToolRunDatapoints

# then clean it up
del importlib
del awsinfo
del grapher
del jobruns
del plots
del toolresources
del toolrundata