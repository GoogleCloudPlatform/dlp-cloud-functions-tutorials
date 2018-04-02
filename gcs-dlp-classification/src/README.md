# Cloud function that uses the Data loss Prevention API to classify files uploaded to a Cloud storage bucket.



Pre-reqs : See the tutorial that accompnaies this example:
https://cloud.google.com/solutions/automating-classification-of-data-uploaded-to-cloud-storage

The workflow:

*   Create Pub/Sub topic & subscription for notification of DLP job completion
*   Associate the Cloud Function with a quarantine bucket
*   Upload files to the quarantine bucket
*   The cloud function is invoked automatically
*   The Data Loss Prevention API inspects and classifies the data
*   The file is moved to the appropriate bucket

## How to run the example

Deploy the Function replacing `[YOUR_QUARANTINE_BUCKET]` with your bucket name:

`gcloud beta functions deploy dlpQuarantineGCS2 --trigger-bucket
[YOUR_QUARANTINE_BUCKET]`

Change directories to the directory that contains the sample data

Upload the sample files to `[YOUR_QUARANTINE_BUCKET]`

`gsutil -m cp * gs://[YOUR_QUARANTINE_BUCKET]/`

## Refs

https://github.com/googleapis/nodejs-dlp

## License

[Apache Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
