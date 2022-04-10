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

variable "project_id" {
description = "Google Project ID."
type        = string
}
variable "gcp_service_list" {
  description = "List of GCP service to be enabled for the project."
  type        = list
}

variable "region" {
description = "Google Cloud region to deploy resources"
type        = string
default     = "europe-west2"
}

variable "pubsub_topic" {
  description = "Pub/Sub topic name"
  type        = string
  default     = "dlp-topic"
}
  
variable "pubsub_subscription" {
  description = "Pub/Sub subscription name"
  type        = string
  default     = "dlp-subscription"
}

variable "dlp_rolesList" {
type =list(string)
default = ["roles/dlp.admin","roles/dlp.serviceAgent"]
}