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

# Enable services in Project.
resource "google_project_service" "gcp_services" {
  count   = length(var.gcp_service_list)
  project = var.project_id
  service = var.gcp_service_list[count.index]

  disable_dependent_services = true
}


# Create bucket to upload data to
resource "google_storage_bucket" "quarantine_bucket" {
  name = "${var.project_id}-quarantine"
  location = var.region 
   uniform_bucket_level_access = true
}

# Create bucket to move sensitive data to 
resource "google_storage_bucket" "sensitive_bucket" {
  name = "${var.project_id}-sensitive"
  location = var.region
   uniform_bucket_level_access = true 
}

# Create bucket to move nonsensitive data to
resource "google_storage_bucket" "non_sensitive_bucket" {
  name = "${var.project_id}-non-sensitive"
  location = var.region
   uniform_bucket_level_access = true 
}

# Create bucket to store cloud function source code
resource "google_storage_bucket" "function_bucket" {
  name = "${var.project_id}-function"
  location = var.region
   uniform_bucket_level_access = true 
}
}


# Create Pub/Sub topic

resource "google_pubsub_topic" "pubsub_topic" {
  name = var.pubsub_topic
  project = var.project_id
}

resource "google_pubsub_subscription" "pubsub_subscription" {
  name  = var.pubsub_subscription
  topic = google_pubsub_topic.pubsub_topic.name

}

# Retrieve default app engine service account

 data "google_app_engine_default_service_account" "default" {
}

output "default_account" {
  value = data.google_app_engine_default_service_account.default.email
}
# Grant DLP permissions to app engine  service account

  resource "google_project_iam_member" "set_dlp_roles" {
  project  =  var.project_id 
  count = length(var.dlp_rolesList)
  role =  var.dlp_rolesList[count.index]
  member   = "serviceAccount:${data.google_app_engine_default_service_account.default.email}"
} 
