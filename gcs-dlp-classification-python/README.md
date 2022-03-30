
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

Update the following user configurable values in the main.py file  

```
[PROJECT_ID_DLP_JOB & TOPIC] Replace with your Project ID 
[YOUR_NON_SENSITIVE_DATA_BUCKET] Replace with the name of the bucket where non sensitive data will be moved to
[YOUR_SENSITIVE_DATA_BUCKET] Replace with the name of the bucket where sensitive data will be moved to
[YOUR_QUARANTINE_BUCKET] Replace with the name of the bucket where you will upload your files to
[PUB/SUB_TOPIC] Replace with your Pub/Sub topic name
```
Deploy the first Function 

`gcloud functions deploy gcs_file_upload_DLP_job --entry-point create_DLP_job --runtime python37 --trigger-resource ${YOUR_QUARANTINE_BUCKET} --trigger-event google.storage.object.finalize `

Deploy the second function

`gcloud functions deploy DLP_pub_classify_file --entry-point resolve_DLP --runtime python37 --trigger-topic ${YOUR_PUB_SUB_TOPIC} `

Change directories to the directory that contains the sample data

Upload the sample files to `${YOUR_QUARANTINE_BUCKET}`

`gsutil -m cp * gs://${YOUR_QUARANTINE_BUCKET}/`

## Refs

https://cloud.google.com/dlp/docs/libraries


## License

[Apache Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
