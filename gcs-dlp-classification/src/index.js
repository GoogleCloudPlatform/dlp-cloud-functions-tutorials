/**
 * Copyright 2017, Google, Inc.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless  required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

// [Optional...?] Start the debug agent
require('@google-cloud/debug-agent').start();

// User-configurable constants
const MIN_LIKELIHOOD = 'LIKELIHOOD_UNSPECIFIED'; // The minimum likelihood required before returning a match
const MAX_FINDINGS = 0; // The maximum number of findings to report (0 = server maximum)
const INFO_TYPES = [{ name: 'PHONE_NUMBER' }, { name: 'EMAIL_ADDRESS' }]; // The infoTypes of information to match
const STAGING_BUCKET = "[YOUR_QUARANTINE_BUCKET]" // The bucket the to-be-scanned files are uploaded to
const NONSENSITIVE_BUCKET = "[YOUR_NON_SENSITIVE_DATA_BUCKET]" // The bucket to move "safe" files to
const SENSITIVE_BUCKET = "[YOUR_SENSITIVE_DATA_BUCKET]" // The bucket to move "unsafe" files to

// Initialize the Google Cloud client libraries
const DLP = require(`@google-cloud/dlp`);
const dlp = new DLP.DlpServiceClient();

const Storage = require(`@google-cloud/storage`);
const storage = Storage();

/**
 * Background Cloud Function to scan a GCS file using the DLP API and move it
 * to another bucket based on the DLP API's findings
 *
 * @param {object} event The Google Cloud Storage event.
 * @param {function} done The Cloud Functions conclusion function.
 */
exports.dlpQuarantineGCS = function (event, done) {
  const file = event.data;

  // Ignore deleted files
  if (file.resourceState === 'not_exists') {
    return done();
  }

  // Get reference to the file to be inspected
  const storageItems = {
    cloudStorageOptions: {
      fileSet: { url: `gs://${file.bucket}/${file.name}` }
    }
  };

  // Construct REST request body for creating an inspect job
  const request = {
    inspectConfig: {
      infoTypes: INFO_TYPES,
      minLikelihood: MIN_LIKELIHOOD,
      maxFindings: MAX_FINDINGS
    },
    storageConfig: storageItems
  };

  // Create a GCS File inspection job and wait for it to complete (using promises)
  dlp.createInspectOperation(request)
    .then((createJobResponse) => {
      const operation = createJobResponse[0];

      // Start polling for job completion
      return operation.promise();
    })
    .then((completeJobResponse) => {
      // When job is complete, get its results
      const jobName = completeJobResponse[0].name;
      return dlp.listInspectFindings({
        name: jobName
      });
    })
    .then((results) => {
      const findings = results[0].result.findings;
      const destBucketName = findings.length > 0 ? SENSITIVE_BUCKET : NONSENSITIVE_BUCKET;
      const destBucket = storage.bucket(destBucketName);

      // Move file to appropriate bucket
      // NOTE: No atomic "move" option exists in GCS, so this may fail to delete the quarantined file
      // TODO possible race condition, if the user deletes the file before the scan finishes
      return storage.bucket(file.bucket).file(file.name).move(destBucket);
    })
    .then(() => {
      done();
    })
    .catch((err) => {
      console.error(err);
      done();
    });
};
