""" Copyright 2018, Google, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless  required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Authors: Yuhan Guo, Zhaoyuan Sun, Fengyi Huang, Weimu Song.
Date:    October 2018

"""

from google.cloud import dlp
from google.cloud import storage
from google.cloud import pubsub
from google.cloud import logging
import os

# ----------------------------
#  User-configurable Constants

PROJECT_ID = os.getenv('DLP_PROJECT_ID', '[PROJECT_ID_DLP_JOB & TOPIC]')
"""The bucket the to-be-scanned files are uploaded to."""
STAGING_BUCKET = os.getenv('QUARANTINE_BUCKET', '[YOUR_QUARANTINE_BUCKET]')
"""The bucket to move "sensitive" files to."""
SENSITIVE_BUCKET = os.getenv('SENSITIVE_DATA_BUCKET', '[YOUR_SENSITIVE_DATA_BUCKET]')
"""The bucket to move "non sensitive" files to."""
NONSENSITIVE_BUCKET = os.getenv('INSENSITIVE_DATA_BUCKET', '[YOUR_NON_SENSITIVE_DATA_BUCKET]')
""" Pub/Sub topic to notify once the  DLP job completes."""
PUB_SUB_TOPIC = os.getenv('PUB_SUB_TOPIC', '[PUB/SUB_TOPIC]')
"""The minimum_likelihood (Enum) required before returning a match"""
"""For more info visit: https://cloud.google.com/dlp/docs/likelihood"""
MIN_LIKELIHOOD = os.getenv('MIN_LIKELIHOOD', 'POSSIBLE')
"""The maximum number of findings to report (0 = server maximum)"""
MAX_FINDINGS = 0
"""The infoTypes of information to match. ALL_BASIC for common infoTypes"""
"""For more info visit: https://cloud.google.com/dlp/docs/concepts-infotypes"""
INFO_TYPES = os.getenv('INFO_TYPES', 'FIRST_NAME,PHONE_NUMBER,EMAIL_ADDRESS,US_SOCIAL_SECURITY_NUMBER').split(',')

APP_LOG_NAME = os.getenv('LOG_NAME', 'DLP-classify-gcs-files')

# End of User-configurable Constants
# ----------------------------------

# Initialize the Google Cloud client libraries
dlp = dlp.DlpServiceClient()
storage_client = storage.Client()
publisher = pubsub.PublisherClient()
subscriber = pubsub.SubscriberClient()

LOG_SEVERITY_DEFAULT = 'DEFAULT'
LOG_SEVERITY_INFO = 'INFO'
LOG_SEVERITY_ERROR = 'ERROR'
LOG_SEVERITY_WARNING = 'WARNING'
LOG_SEVERITY_DEBUG = 'DEBUG'


def log(text, severity=LOG_SEVERITY_DEFAULT, log_name=APP_LOG_NAME):
    logging_client = logging.Client()
    logger = logging_client.logger(log_name)

    return logger.log_text(text, severity=severity)


def create_DLP_job(data, done):
    """This function is triggered by new files uploaded to the designated Cloud Storage quarantine/staging bucket.

         It creates a dlp job for the uploaded file.
      Arg:
         data: The Cloud Storage Event
      Returns:
          None. Debug information is printed to the log.
      """
    # Get the targeted file in the quarantine bucket
    file_name = data['name']
    log('Function triggered for file [{}] to start a DLP job of InfoTypes [{}]'.format(file_name, ','.join(INFO_TYPES)),
        severity=LOG_SEVERITY_INFO)

    # Prepare info_types by converting the list of strings (INFO_TYPES) into a list of dictionaries
    info_types = [{'name': info_type} for info_type in INFO_TYPES]

    # Convert the project id into a full resource id.
    parent = f"projects/{PROJECT_ID}"

    # Construct the configuration dictionary.
    inspect_job = {
        'inspect_config': {
            'info_types': info_types,
            'min_likelihood': MIN_LIKELIHOOD,
            'limits': {
                'max_findings_per_request': MAX_FINDINGS
            },
        },
        'storage_config': {
            'cloud_storage_options': {
                'file_set': {
                    'url':
                        'gs://{bucket_name}/{file_name}'.format(
                            bucket_name=STAGING_BUCKET, file_name=file_name)
                }
            }
        },
        'actions': [{
            'pub_sub': {
                'topic':
                    'projects/{project_id}/topics/{topic_id}'.format(
                        project_id=PROJECT_ID, topic_id=PUB_SUB_TOPIC)
            }
        }]
    }

    # Create the DLP job and let the DLP api processes it.
    try:
        dlp.create_dlp_job(parent=(parent), inspect_job=(inspect_job))
        log('Job created by create_DLP_job', severity=LOG_SEVERITY_INFO)
    except Exception as e:
        log(e, severity=LOG_SEVERITY_ERROR)


def resolve_DLP(data, context):
    """This function listens to the pub/sub notification from function above.

      As soon as it gets pub/sub notification, it picks up results from the
      DLP job and moves the file to sensitive bucket or nonsensitive bucket
      accordingly.
      Args:
          data: The Cloud Pub/Sub event

      Returns:
          None. Debug information is printed to the log.
      """
    # Get the targeted DLP job name that is created by the create_DLP_job function
    job_name = data['attributes']['DlpJobName']
    log('Received pub/sub notification from DLP job: {}'.format(job_name), severity=LOG_SEVERITY_INFO)

    # Get the DLP job details by the job_name
    job = dlp.get_dlp_job(request={'name': job_name})
    log('Job Name:{name}\nStatus:{status}'.format(name=job.name, status=job.state), severity=LOG_SEVERITY_INFO)

    # Fetching Filename in Cloud Storage from the original dlpJob config.
    # See defintion of "JSON Output' in Limiting Cloud Storage Scans':
    # https://cloud.google.com/dlp/docs/inspecting-storage

    file_path = (
        job.inspect_details.requested_options.job_config.storage_config
            .cloud_storage_options.file_set.url)
    file_name = file_path.split("/", 3)[3]

    info_type_stats = job.inspect_details.result.info_type_stats
    source_bucket = storage_client.get_bucket(STAGING_BUCKET)
    source_blob = source_bucket.blob(file_name)
    if (len(info_type_stats) > 0):
        # Found at least one sensitive data
        for stat in info_type_stats:
            log('Found {stat_cnt} instances of {stat_type_name}.'.format(
                stat_cnt=stat.count, stat_type_name=stat.info_type.name), severity=LOG_SEVERITY_WARNING)
        log('Moving item to sensitive bucket', severity=LOG_SEVERITY_DEBUG)
        destination_bucket = storage_client.get_bucket(SENSITIVE_BUCKET)
        source_bucket.copy_blob(source_blob, destination_bucket,
                                file_name)  # copy the item to the sensitive bucket
        source_blob.delete()  # delete item from the quarantine bucket

    else:
        # No sensitive data found
        log('Moving item to non-sensitive bucket', severity=LOG_SEVERITY_DEBUG)
        destination_bucket = storage_client.get_bucket(NONSENSITIVE_BUCKET)
        source_bucket.copy_blob(
            source_blob, destination_bucket,
            file_name)  # copy the item to the non-sensitive bucket
        source_blob.delete()  # delete item from the quarantine bucket
    log('classifying file [{}] Finished'.format(file_name), severity=LOG_SEVERITY_DEBUG)
