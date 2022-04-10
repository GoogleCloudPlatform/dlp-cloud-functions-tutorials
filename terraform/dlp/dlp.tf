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

# Retrieve project number

data "google_project" "project" {
}

output "project_number" {
  value = data.google_project.project.number
}

 # Grant viewer role to DLP service agent
 # https://cloud.google.com/dlp/docs/iam-permissions#service_account 

resource "google_project_iam_member" "set_viewer_role" {
  project  =  var.project_id 
  role =  "roles/viewer"
  member   = "serviceAccount:service-${data.google_project.project.number}@dlp-api.iam.gserviceaccount.com" 
} 