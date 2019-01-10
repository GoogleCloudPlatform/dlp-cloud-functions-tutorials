
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

Deploy the first Function replacing `[YOUR_QUARANTINE_BUCKET]` with your bucket name:

`gcloud functions deploy create_DLP_job --runtime python37 --trigger-resource [YOUR_QUARANTINE_BUCKET] --trigger-event google.storage.object.finalize`

Deploy the second function replacing  `[PUB/SUB TOPIC]` with ypur pub/sub topic

`gcloud functions deploy resolve_DLP --runtime python37 --trigger-topic [PUB/SUB TOPIC]`

Change directories to the directory that contains the sample data

Upload the sample files to `[YOUR_QUARANTINE_BUCKET]`

`gsutil -m cp * gs://[YOUR_QUARANTINE_BUCKET]/`

## Refs

https://cloud.google.com/dlp/docs/libraries

## Notes

Resolves the time-out issue of the Node.JS example when analyzing a file that is larger than 200MB.

## License

[Apache Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
