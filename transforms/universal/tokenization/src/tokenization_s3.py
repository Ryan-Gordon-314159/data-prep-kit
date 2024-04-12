# (C) Copyright IBM Corp. 2024.
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import os
import sys

from data_processing.ray import TransformLauncher
from data_processing.utils import DPLConfig, ParamsUtils
from tokenization_transform import TokenizationTransformConfiguration


print(os.environ)
# create launcher
launcher = TransformLauncher(transform_runtime_config=TokenizationTransformConfiguration())
# create parameters
s3_cred = {
    "access_key": DPLConfig.S3_ACCESS_KEY,
    "secret_key": DPLConfig.S3_SECRET_KEY,
    "url": "https://s3.us-east.cloud-object-storage.appdomain.cloud",
}
tkn_params = {
    "tkn_tokenizer": "hf-internal-testing/llama-tokenizer",
    "tkn_doc_id_column": "document_id",
    "tkn_doc_content_column": "contents",
    "tkn_text_lang": "en",
    "tkn_chunk_size": 0,
}
s3_conf = {
    "input_folder": "cos-optimal-llm-pile/bluepile-processing/xh/opensource/input/",
    "output_folder": "cos-optimal-llm-pile/bluepile-processing/xh/opensource/output/",
}
worker_options = {"num_cpus": 0.8}
code_location = {"github": "github", "commit_hash": "12345", "path": "path"}
params = {
    # where to run
    "run_locally": True,
    # Data access. Only required parameters are specified
    "data_s3_cred": ParamsUtils.convert_to_ast(s3_cred),
    "data_s3_config": ParamsUtils.convert_to_ast(s3_conf),
    # orchestrator
    "worker_options": ParamsUtils.convert_to_ast(worker_options),
    "num_workers": 5,
    "pipeline_id": "pipeline_id",
    "job_id": "job_id",
    "creation_delay": 0,
    "code_location": ParamsUtils.convert_to_ast(code_location),
}

sys.argv = ParamsUtils.dict_to_req(d=params | tkn_params)
launcher.launch()
