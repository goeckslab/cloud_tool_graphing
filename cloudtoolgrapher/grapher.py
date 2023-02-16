import sys

from .awsinfo import AWSInfo
from .toolrundata import ToolRunDatapoints
from .toolresources import ToolResourceRequests
from .plots import ToolPlot, DeltaPlot
from .jobruns import JobRuns

def graph(args):
  job_conf, job_info = args
  print("\nFetching AWS Info...")
  aws_itypes = AWSInfo()

  print("\nGenerating datapoints from source files...")
  trr = ToolResourceRequests(job_conf)
  jr = JobRuns(job_info)
  trd = ToolRunDatapoints(trr, jr)
  
  print("\nCreating Memory Delta plot")
  DeltaPlot(trd).to_html('memorydelta.html')
  
  print("\nCreating tool plots...")
  for tool_id in trd.get_tools():
    print(f"{tool_id}", sep=" ... ")
    ToolPlot(tool_id, trd, aws_itypes).to_html(f"{tool_id}.html")

  with open('index.html', 'w') as idx:
    idx.write("""<html>
<title>Cloud Tool Usage Stats Index</title>
<body>
<h2>Tool Run Data</h2>
<ul>
  <li><a target=\"_blank\" href="memorydelta.html">Memory Delta: GB RAM requested - used</a></li>
""")
    for tool_id in trd.get_tools():
        idx.write(f"  <li><a target=\"_blank\" href=\"{tool_id}.html\">{tool_id} runs</a></li>\n")
    idx.write("""</ul>
</body>
</html>
""")