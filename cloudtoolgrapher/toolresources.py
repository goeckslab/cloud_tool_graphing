import xml.etree.ElementTree as et

class ToolResourceRequests:

  def __init__(self, gxy_job_conf_path: str) -> None:
    # load in job conf with tool and destination info
    _job_conf = et.parse(gxy_job_conf_path)
    _tool_to_dest_dict = {x.attrib['id']: x.attrib['destination'] for x in _job_conf.getroot().iter('tool')}

    def get_from_elem(param, dest_elem: et.Element) -> float: #get parameter values for destination entries
      r = -1
      for x in dest_elem.iter('param'):
          if x.attrib["id"] == param:
              r = float(x.text)
      assert(r > 0)
      return r

    _dest_to_resource_request = {
      x.attrib["id"] : {
        "vcpus": get_from_elem('vcpu', x),
        "memory": get_from_elem('memory', x)
      } for x in _job_conf.getroot().iter('destination') if x.attrib['runner'][:4] == "aws_"
    }

    self._tool_resource_request = {
      x: _dest_to_resource_request[_tool_to_dest_dict[x]] for x in _tool_to_dest_dict if _tool_to_dest_dict[x] != "aws_batch_entry" #skip this destination for now
    }

  def get_resources(self, tool_id: str) -> dict:
    return self._tool_resource_request[tool_id]

  def get_tool_ids(self):
    return self._tool_resource_request.keys()