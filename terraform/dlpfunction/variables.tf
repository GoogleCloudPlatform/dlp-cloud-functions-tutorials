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

variable "function_name_01" {
  description = " 1st Function name"
  type        = string
  default     = "create_DLP_job"
}
variable "function_01_entry_point" {
  description = " 1st Function entry point"
  type        = string
  default     = "create_DLP_job"
}

variable "function_name_02" {
  description = " 2nd Function name"
  type        = string
  default     = "resolve_DLP"
}
variable "function_02_entry_point" {
  description = " 2nd Function entry point"
  type        = string
  default     = "resolve_DLP"
}