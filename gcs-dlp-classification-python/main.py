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
import os

# ----------------------------
#  User-configurable Constants

PROJECT_ID = '[PROJECT_ID_HOSTING_STAGING_BUCKET]'
"""The bucket the to-be-scanned files are uploaded to."""
STAGING_BUCKET = '[YOUR_QUARANTINE_BUCKET]'
"""The bucket to move "sensitive" files to."""
SENSITIVE_BUCKET = '[YOUR_SENSITIVE_DATA_BUCKET]'
"""The bucket to move "non sensitive" files to."""
NONSENSITIVE_BUCKET = '[YOUR_NON_SENSITIVE_DATA_BUCKET]'
""" Pub/Sub topic to notify once the  DLP job completes."""
PUB_SUB_TOPIC = '[PUB/SUB_TOPIC]'
"""The minimum_likelihood (Enum) required before returning a match"""
"""For more info visit: https://cloud.google.com/dlp/docs/likelihood"""
MIN_LIKELIHOOD = 'POSSIBLE'
"""The maximum number of findings to report (0 = server maximum)"""
MAX_FINDINGS = 0
"""The infoTypes of information to match"""
"""For more info visit: https://cloud.google.com/dlp/docs/concepts-infotypes"""
INFO_TYPES = [
    'FIRST_NAME', 'PHONE_NUMBER', 'EMAIL_ADDRESS', 'US_SOCIAL_SECURITY_NUMBER'
]

# End of User-configurable Constants
# ----------------------------------

# Initialize the Google Cloud client libraries
dlp = dlp.DlpServiceClient()
storage_client = storage.Client()
publisher = pubsub.PublisherClient()
subscriber = pubsub.SubscriberClient()


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
  print('Function triggered for file [{}]'.format(file_name))

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
    print('Job created by create_DLP_job')
  except Exception as e:
    print(e)


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
  print('Received pub/sub notification from DLP job: {}'.format(job_name))

  # Get the DLP job details by the job_name
  job = dlp.get_dlp_job(request = {'name': job_name})
  print('Job Name:{name}\nStatus:{status}'.format(
      name=job.name, status=job.state))

  # Fetching Filename in Cloud Storage from the original dlpJob config.
  # See defintion of "JSON Output' in Limiting Cloud Storage Scans':
  # https://cloud.google.com/dlp/docs/inspecting-storage

  file_path = (
      job.inspect_details.requested_options.job_config.storage_config
      .cloud_storage_options.file_set.url)
  file_name = os.path.basename(file_path)

  info_type_stats = job.inspect_details.result.info_type_stats
  source_bucket = storage_client.get_bucket(STAGING_BUCKET)
  source_blob = source_bucket.blob(file_name)
  if (len(info_type_stats) > 0):
    # Found at least one sensitive data
    for stat in info_type_stats:
      print('Found {stat_cnt} instances of {stat_type_name}.'.format(
          stat_cnt=stat.count, stat_type_name=stat.info_type.name))
    print('Moving item to sensitive bucket')
    destination_bucket = storage_client.get_bucket(SENSITIVE_BUCKET)
    source_bucket.copy_blob(source_blob, destination_bucket,
                            file_name)  # copy the item to the sensitive bucket
    source_blob.delete()  # delete item from the quarantine bucket

  else:
    # No sensitive data found
    print('Moving item to non-sensitive bucket')
    destination_bucket = storage_client.get_bucket(NONSENSITIVE_BUCKET)
    source_bucket.copy_blob(
        source_blob, destination_bucket,
        file_name)  # copy the item to the non-sensitive bucket
    source_blob.delete()  # delete item from the quarantine bucket
  print('{} Finished'.format(file_name))
