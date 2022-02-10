
# Cloud function that uses the Data loss Prevention API to classify files uploaded to a Cloud storage bucket

Pre-reqs : See the tutorial that accompanies this example:
https://cloud.google.com/solutions/automating-classification-of-data-uploaded-to-cloud-storage

The workflow:

* Grant Cloud IAM permissions to service accounts (Refer to tutorial)
* Create 3 Cloud Storage buckets
* Create Cloud Pub/Sub topic & subscription for notification of DLP job completion
* Replace variables in the Cloud function file with your values
* Associate the 1st Cloud Function with a designated quarantine/Staging bucket
* Associate the 2nd Cloud Function with a Pub/Sub topic
* Upload files to the quarantine bucket
* The cloud functions are invoked automatically
* The Data Loss Prevention API inspects and classifies the data
* The file is moved to the appropriate bucket

## How to run the example

Deploy the first Function setting the following environment variables. the topic does not contain project_id

```
YOUR_PUB_SUB_TOPIC=
YOUR_NON_SENSITIVE_DATA_BUCKET=
YOUR_SENSITIVE_DATA_BUCKET=
YOUR_QUARANTINE_BUCKET=
YOUR_DLP_PUB_SUB_TOPIC_PROJECT_ID=
```

`gcloud functions deploy gcs_file_upload_DLP_job --entry-point create_DLP_job --runtime python37 --trigger-resource ${YOUR_QUARANTINE_BUCKET} --trigger-event google.storage.object.finalize --set-env-vars=DLP_PROJECT_ID=${YOUR_DLP_PUB_SUB_TOPIC_PROJECT_ID} --set-env-vars=QUARANTINE_BUCKET=${YOUR_QUARANTINE_BUCKET} --set-env-vars=SENSITIVE_DATA_BUCKET=${YOUR_SENSITIVE_DATA_BUCKET} --set-env-vars=INSENSITIVE_DATA_BUCKET=${YOUR_NON_SENSITIVE_DATA_BUCKET} --set-env-vars=PUB_SUB_TOPIC=${YOUR_PUB_SUB_TOPIC} `

Deploy the second function

`gcloud functions deploy DLP_pub_classify_file --entry-point resolve_DLP --runtime python37 --trigger-topic ${YOUR_PUB_SUB_TOPIC} --set-env-vars=DLP_PROJECT_ID=${YOUR_DLP_PUB_SUB_TOPIC_PROJECT_ID} --set-env-vars=QUARANTINE_BUCKET=${YOUR_QUARANTINE_BUCKET} --set-env-vars=SENSITIVE_DATA_BUCKET=${YOUR_SENSITIVE_DATA_BUCKET} --set-env-vars=INSENSITIVE_DATA_BUCKET=${YOUR_NON_SENSITIVE_DATA_BUCKET} --set-env-vars=PUB_SUB_TOPIC=${YOUR_PUB_SUB_TOPIC}`

Change directories to the directory that contains the sample data

Upload the sample files to `${YOUR_QUARANTINE_BUCKET}`

`gsutil -m cp * gs://${YOUR_QUARANTINE_BUCKET}/`

## Refs

https://cloud.google.com/dlp/docs/libraries

## Notes

Resolves the time-out issue of the Node.JS example when analyzing a file that is larger than 200MB.

## License

[Apache Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
