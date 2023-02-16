import sys

from .grapher import graph


def main():
  args=['minified_job_conf.xml','job_metrics_sample.tsv']

  if len(sys.argv) != 3 or sys.argv[1] in ('-h', '--help'):
    print(f"""
    Usage:
      {sys.argv[0]} <galaxy job conf file> <job metrics file>
      without arguments, defaults to: {args} 
    """)
    if len(sys.argv) != 1:
      exit()    
    print(f"...using defaults {args}")

  for i, arg in enumerate(sys.argv[1:3]):
    args[i]=arg
  graph(args)