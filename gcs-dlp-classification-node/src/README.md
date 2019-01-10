# Cloud function that uses the Data loss Prevention API to classify files uploaded to a Cloud storage bucket.



Pre-reqs : See the tutorial that accompanies the Python classification example:
https://cloud.google.com/solutions/automating-classification-of-data-uploaded-to-cloud-storage

The workflow:

*   Grant Cloud IAM permissions to service accounts (Refer to tutorial)
*   Create 3 Cloud Storage buckets
*   Create Cloud Pub/Sub topic & subscription for notification of DLP job completion
*   Replace variables in the Cloud function file with your values
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

## Notes

This example is a simple one-function demonstration/proof-of-concept. Its is not suitable for production. If you see any time out issues please adjust the Cloud Functions timeout value  to ~5 min instead of 60 seconds.

## License

[Apache Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
