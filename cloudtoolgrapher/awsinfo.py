import boto3
import json


class AWSInfo:
  DEFAULT_REGION = 'us-west-2'
  #note, from aws docs, families pulled with 'optimal best fit' strategy we've set:  "C4, M4, and R4"

  def __init__(self, region=None):
    region = region if region else self.DEFAULT_REGION 

    self._types = {}
    prices = self.get_prices()
    def type_extraction(**kwargs):
      itypes = boto3.client('ec2', region_name=region).describe_instance_types(
        **{
          'Filters':[
            {
              'Name': 'instance-type',
              'Values': [
                '?4.*',
              ]
            },
          ]
        }, **kwargs
      )
      for itype in itypes['InstanceTypes']:
        self._types[itype['InstanceType']] = {
          'default_vcpus': itype['VCpuInfo']['DefaultVCpus'],
          'memory_in_mib': itype['MemoryInfo']['SizeInMiB'],
          'usd_per_hour': prices[itype['InstanceType']]
        }
      try:
        type_extraction(**{'NextToken': itypes['NextToken']}) if itypes['NextToken'] else None
      except KeyError:
        return
    type_extraction()

  @staticmethod
  def get_prices(instance_types_filter=lambda x: x[:3] in ['c4.', 'm4.', 'r4.']):
    pc = boto3.client('pricing', region_name='us-east-1') # region here isn't the region of interest but where the API lives

    filtervals = {
      'marketoption':'OnDemand',
      'regionCode':'us-west-2',
      'preInstalledSw':'NA',
      'tenancy': "shared",
      'capacityStatus': 'Used',
      'operatingSystem': "Linux"
    }

    pricefilter = [{
        'Type': 'TERM_MATCH',
        'Field': field,
        'Value': value
    } for field, value in filtervals.items()]

    nt = {} # no next token to start
    ps = {}
    while True:
      values = pc.get_products(ServiceCode='AmazonEC2', Filters=pricefilter, **nt)
      for x in values['PriceList']:
          x = json.loads(x) # str to dict
          it = x['product']['attributes']['instanceType']
          if instance_types_filter(it):
            od = x['terms']['OnDemand']
            id1 = list(od)[0]
            id2 = list(od[id1]['priceDimensions'])[0]
            ps[it] = od[id1]['priceDimensions'][id2]['pricePerUnit']['USD']
      nt = {"NextToken":values['NextToken']} if 'NextToken' in values else None
      if not nt:
          break
    return ps

  def get_closest_match(self, memory, vcpus):
    closest = {}

    def match(requested_memory, requested_vcpus, actual_itype, closest=None):
      actual_iname = next(iter(actual_itype.keys()))
      actual_ivcpus = float(actual_itype[actual_iname]['default_vcpus'])
      actual_imem = float(actual_itype[actual_iname]['memory_in_mib'])/1024 # to GB
      # is this smaller than the instance stats? a match
      if (
        (
          requested_memory <= actual_imem and 
          requested_vcpus < actual_ivcpus
        ) or (
          requested_memory < actual_imem and 
          requested_vcpus <= actual_ivcpus
        )
      ):
        # ...but is the instance smaller than the closest so far?
        return True if not closest else match(
          actual_imem,
          actual_ivcpus,
          closest
        )
      return False

    for x in self._types:
      if match(memory, vcpus, {x:self._types[x]}, closest):
        closest = {x:self._types[x]}
    return closest

  def get_instance_types(self):
    return [key for key in self._types.keys()]

  def get_all_instance_info(self):
    return self._types

  def get_instance_info(self, itype):
    return self._types[itype]
