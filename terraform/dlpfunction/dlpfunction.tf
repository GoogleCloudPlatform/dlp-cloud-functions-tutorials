/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

# Google Provider

provider "google" {
project = var.project_id
region  = var.region
} 


# Creates zip file of function code & requirments.txt
data "archive_file" "source" {
    type        = "zip"
    source_dir  = "../src"
    output_path = "/tmp/dlpfunction.zip"
}


# Add zip file to the Cloud Function's source code bucket
resource "google_storage_bucket_object" "zip" {
    source       = data.archive_file.source.output_path
    content_type = "application/zip"
    # Append to  MD5 checksum of the files's content to force the zip to be updated as soon as a change occurs
    name         = "src-${data.archive_file.source.output_md5}.zip"
    bucket       = "${var.project_id}-function"

} 

# Create 1st Cloud function triggered by a `Finalize` event on the quarantine bucket
resource "google_cloudfunctions_function" "function" {
    name                  = var.function_name_01
    runtime               = "python37"  

    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = "${var.project_id}-function"
    source_archive_object = google_storage_bucket_object.zip.name

    # Entry point of  the function name in the cloud function `main.py` source code
    entry_point      = "create_DLP_job"
    
    event_trigger {
        event_type = "google.storage.object.finalize"
        resource   = "${var.project_id}-quarantine"  # quarantine bucket where files are uploaded for processing
    }
}

# Create 2nd Cloud function triggered by a publish event on the Pub/Sub topic
resource "google_cloudfunctions_function" "pubsub-function" {
    name                  = var.function_name_02
    runtime               = "python37"  

    # Get the source code of the cloud function as a Zip compression
    source_archive_bucket = "${var.project_id}-function"
    source_archive_object = google_storage_bucket_object.zip.name

    # Entry point of  the function name in the cloud function `main.py` source code
    entry_point      = var.function_02_entry_point
    
    event_trigger {
        event_type = "google.pubsub.topic.publish"
        resource   = "projects/${var.project_id}/topics/${var.pubsub_topic}"   
    }
}