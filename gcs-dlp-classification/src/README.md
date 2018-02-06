# Cloud function that uses the Data loss Prevention API to classify files uploaded to a Cloud storage bucket. 



The following code accompanies the [tutorial] ( TODO: Link to be added)  - which includes the full walkthrough

Pre-reqs : See tutorial

The workflow: 
* Associate the Cloud Function with a quarantine bucket
* Upload files to the quarantine bucket
* Invoke the cloud function 
* The Data Loss Prevention API inspects and classifies the data
* The file is moved to the appropriate bucket
 
## How to run the example

Deploy the Function replacing [YOUR_QUARANTINE_BUCKET]with your bucket name:

`gcloud beta functions deploy dlpQuarantineGCS --trigger-bucket [YOUR_QUARANTINE_BUCKET]`

Change directories to the directory that contains the sample data

Upload the sample files to  [YOUR_QUARANTINE_BUCKET]

`gsutil -m  cp * gs://[YOUR_QUARANTINE_BUCKET]/ `


## Refs


https://cloud.google.com/nodejs/docs/reference/dlp/0.2.x/


## License

[Apache Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
