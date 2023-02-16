from .toolresources import ToolResourceRequests
from .jobruns import JobRuns

class ToolRunDatapoints:

  def __init__(self, trr:ToolResourceRequests, jr:JobRuns):
    tools_intersection = set(trr.get_tool_ids()).intersection(set(jr.get_tool_ids()))
    def _add_deltas(runs, resources):
      return [
        {
          **run,
          'slots_delta': resources['vcpus'] - run['vcpus'],
          'memory_mb_delta': resources['memory'] - run['memory_mb'],
          'requested_memory_mb': resources['memory'],
          'requested_slots': resources['vcpus']
        } for run in runs
      ]

    self._runs = {
      tool_id: _add_deltas(jr.get_runs(tool_id), trr.get_resources(tool_id))
      for tool_id in tools_intersection
    }

  def get_tools(self):
    return self._runs.keys()

  def runs_by_tool(self, tool_id, sorted_by="create_time"):
    return sorted(self._runs[tool_id], key=lambda x:x[sorted_by])