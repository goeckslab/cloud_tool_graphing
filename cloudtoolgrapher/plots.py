import plotly.express as px
import plotly.graph_objs as go

from .awsinfo import AWSInfo
from .toolrundata import ToolRunDatapoints


class BasePlot:

  def show(self):
    self.fig.show()
  
  def to_html(self, filename):
    self.fig.write_html(filename)


class DeltaPlot(BasePlot):
  def __init__(self, trd: ToolRunDatapoints):
    self.fig = px.scatter()
    self.fig.update_layout(
      title="Delta Memory: (GB Requested - GB Used) Per Tool Run",
      xaxis_title="Date of job execution",
      yaxis_title="Difference between requested and used memory in GB of RAM "
    )
    lines = []
    for tool in trd.get_tools():
      x = []
      y = []
      
      for run in trd.runs_by_tool(tool):
        x.append(run['create_time'])
        y.append(run['memory_mb_delta']/1024)
      
      lines.append({'x': x, 'y': y, 'name': f"{tool}", 'mode': 'lines+markers'})
    
    for line in lines:
      self.fig.add_trace(
        go.Scatter(
          x = line['x'],
          y = line['y'],
          name = line['name'],
          legendgroup = "tools",
          legendgrouptitle_text = "Tool IDs"
        )
      )

class ToolPlot(BasePlot):
  def __init__(self, tool_id, trd:ToolRunDatapoints, aws_info: AWSInfo):
    self.fig = px.scatter()
    self.fig.update_layout(
      title=f"Job execution details for {tool_id}",
      xaxis_title="Date of job execution",
      yaxis_title="GB of RAM "
    )
    lines = []
    x = []
    y_predicted = []
    y_actual = []
    y_requested = []
    y_cost = []
    # basic data
    for run in trd.runs_by_tool(tool_id):
      x.append(run['create_time'])
      y_predicted.append(run['predicted_mem_gb'])
      y_actual.append(run['memory_mb']/1024) # to GB
      y_requested.append(run['requested_memory_mb']/1024)
      itype_guess = aws_info.get_closest_match(
        run['requested_memory_mb']/1024,
        run['vcpus']
      )
      y_cost.append(float(itype_guess.popitem()[1]['usd_per_hour'])*run['runtime_hrs'])
    lines.append({'x': x, 'y': y_actual, 'name': f"{tool_id} - actual", 'mode': 'lines+markers'})
    lines.append({'x': x, 'y': y_requested, 'name': f"{tool_id} - requested", 'mode': 'lines+markers'})
    if y_predicted:
      lines.append({'x': x, 'y': y_predicted, 'name': f"{tool_id} - predicted", 'mode': 'lines+markers'}) 
    for line in lines:
      self.fig.add_trace(
        go.Scatter(
          x = line['x'],
          y = line['y'],
          name = line['name'],
        )
      )