import pandas as pd

class JobRuns:

  BYTES_IN_MB=1024**2

  DEFAULT_TOOL_ALLOWLIST = ['ludwig_render_config', 'unmicst', 'quantification',
                            'vitessce_spatial', 'ashlar', 'scimap_mcmicro_to_anndata',
                            'basic_illumination', 's3segmenter', 'ludwig_train',
                            'scimap_phenotyping', 'mesmer', 'unet_coreograph',
                            'interactive_tool_bam_iobio', 'ludwig_visualize', 'ludwig_experiment',
                            'rename_tiff_channels', 'ip_convertimage', 'interactive_tool_oncogene',
                            'squidpy_spatial', 'gate_finder', 'scimap_spatial',
                            'sklearn_searchcv', 'sklearn_build_pipeline', 'Summary_Statistics1',
                            'cell_intensity_processing', 'cp_segmentation', 'anndata_manipulate',
                            'interactive_tool_bam_iobio_ecr', 'ludwig_hyperopt', 'interactive_tool_bam_iobio_ecr_public',
                            'sklearn_feature_selection', 'vcf_to_maf_customtrack1']

  FEATURES_OF_INTEREST = [
    'tool_id',
    'total_filesize',
    'slots',
    'memory_bytes',
    'create_time',
    'state',
    'runtime_seconds'
    ]

  TOOL_LAMBDAS = {
    "mesmer": lambda x: 3.238 * x + 2.641 * 10**9,
    "unmicst": lambda x: 0.5287 * x + 2.2412 * 10**9,
    "s3segmenter": lambda x: 0.5343 * x + 1.1870 * 10**9,
    "quantification": lambda x: 0.8753 * x + 0.5243 * 10**9,
    "scimap_phenotyping": lambda x: 8.8367 * x + 0.2541 * 10**9,
    "scimap_spatial": lambda x: 8.8367 * x + 0.2541 * 10**9,
    "vitessce_spatial": lambda x: 0.4143 * x + 1.3076 * 10**9,
    # Machine learning
    "ludwig_evaluate": lambda x: 10 * x + 10**9,
    "ludwig_experiment": lambda x: 10 * x + 10**9,
    "ludwig_hyperopt": lambda x: 10 * x + 10**9,
    "ludwig_predict": lambda x: 10 * x + 10**9,
    "ludwig_train": lambda x: 10 * x + 10**9,
    "keras_image_deep_learning": lambda x: 10 * x + 10**9,
    "sklearn_fitted_model_eval": lambda x: 10 * x + 10**9,
    "keras_train_and_eval": lambda x: 10 * x + 10**9,
    "model_prediction": lambda x: 10 * x + 10**9,
    "sklearn_model_validation": lambda x: 10 * x + 10**9,
    "sklearn_searchcv": lambda x: 10 * x + 10**9,
}

  def __init__(self, gxadmin_job_metrics_file:str, filter_out=None, tool_allowlist=None) -> None:
    if not tool_allowlist:
      tool_allowlist = self.DEFAULT_TOOL_ALLOWLIST
    if not filter_out:
      filter_out = self.default_filter
    # get columns for the converter to clean column names in the data frame
    with open(gxadmin_job_metrics_file) as f:
      columns = f.readline()[:-1].split("|") # get the header line, remove trailing newline, split by separator
    # read the file, strip values of whitespace
    _gxadmin_data = pd.read_csv(
      gxadmin_job_metrics_file, 
      sep='|', 
      converters={col: str.strip for col in columns}, 
      skiprows=[1])
    # strip the column names
    _gxadmin_data = _gxadmin_data.rename(columns={
      x: x.strip() for x in _gxadmin_data.columns
    })

    self._job_runs = {}

    for idx in range(len(_gxadmin_data)):
      row = { param : _gxadmin_data.at[idx, param] for param in self.FEATURES_OF_INTEREST }
      if filter_out(row):
        continue
      
      base_tool_id, tool_version = row['tool_id'].split('/')[-2:] if '/' in row['tool_id'] else (row['tool_id'], None)
      if base_tool_id not in tool_allowlist:
        continue
      dynamic_dest_prediction_gbs = (
        self.TOOL_LAMBDAS[base_tool_id](float(row["total_filesize"]))/10**9 if
        base_tool_id in self.TOOL_LAMBDAS else
        None
      )
      addendum = {
        "tool_version": tool_version,
        "filesize_mb": float(row["total_filesize"])/self.BYTES_IN_MB,
        "vcpus": float(row["slots"]),
        "memory_mb": float(row["memory_bytes"])/self.BYTES_IN_MB,
        "create_time": row["create_time"],
        "runtime_hrs": float(row['runtime_seconds'])/360,
        "predicted_mem_gb": dynamic_dest_prediction_gbs
      }
      try:
        self._job_runs[base_tool_id].append(addendum)
      except KeyError:
        self._job_runs[base_tool_id] = [addendum]

  @staticmethod
  def default_filter(row):
    if (row['state'] != 'ok' or 
        not row['slots'] or
        not row['memory_bytes'] or
        not row['total_filesize']
      ):
      return True
    return False

  def get_runs(self, tool_id):
    return self._job_runs[tool_id]
  
  def get_tool_ids(self):
    return self._job_runs.keys()

  def _cleanup(self):
    #TODO, maybe: use true CSVs, clean up dumb ones that have tons of whitespace etc
    pass