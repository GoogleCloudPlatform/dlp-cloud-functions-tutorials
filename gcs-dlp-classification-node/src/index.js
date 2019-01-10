/**
 * Copyright 2018, Google, Inc.
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

// Start the debug agent. Remove or comment out if not required
require('@google-cloud/debug-agent').start();


// User-configurable constants:

// The minimum likelihood required before returning a match
const MIN_LIKELIHOOD = 'LIKELIHOOD_UNSPECIFIED';

// The maximum number of findings to report (0 = server maximum)
const MAX_FINDINGS = 0;

// The infoTypes of information to match
const INFO_TYPES = [
  { name: 'PHONE_NUMBER' },
  { name: 'EMAIL_ADDRESS' },
  { name: 'US_SOCIAL_SECURITY_NUMBER' }
];

// The bucket the to-be-scanned files are uploaded to
const STAGING_BUCKET = '[YOUR_QUARANTINE_BUCKET]';
// The bucket to move "safe" files to
const NONSENSITIVE_BUCKET = '[YOUR_NON_SENSITIVE_DATA_BUCKET]';

// The bucket to move "unsafe" files to
const SENSITIVE_BUCKET = '[YOUR_SENSITIVE_DATA_BUCKET]';

// The project ID to run the DLP API call under
const PROJECT_ID = '[PROJECT_ID HOSTING STAGING_BUCKET]';

// Cloud Pub/Sub topic to notify once the  DLP job completes
const PUB_SUB_TOPIC = '[PUB/SUB TOPIC]';

// Cloud Pub/Sub subscription to use when listening for job complete notifications
const PUB_SUB_SUBSCR = '[PUB/SUB SUBSCRIPTION]';


// Initialize the Google Cloud client libraries
const DLP = require('@google-cloud/dlp');
const dlp = new DLP.DlpServiceClient();

const Storage = require('@google-cloud/storage');
const storage = Storage();

const Pubsub = require('@google-cloud/pubsub');
const pubsub = new Pubsub();

/**
 * Background Cloud Function to scan a Cloud Storage file using the DLP API and move it
 * to another bucket based on the DLP API's findings
 *
 * @param {object} event The Cloud Storage event.
 * @param {function} callback Called at completion of processing the file.
 */
exports.dlpQuarantineGCS = (event, callback) => {
    var file = event.data;
    console.log('Processing file: ' + file.name);
    setTimeout(() => inspectGCSFile(
      PROJECT_ID,
      file.bucket,
      file.name,
      PUB_SUB_TOPIC,
      PUB_SUB_SUBSCR,
      MIN_LIKELIHOOD,
      MAX_FINDINGS,
      INFO_TYPES,
      callback
    ), 2000);
};

function inspectGCSFile(
    projectId,
    bucketName,
    fileName,
    topicId,
    subscriptionId,
    minLikelihood,
    maxFindings,
    infoTypes,
    done) {
  // Get reference to the file to be inspected
  const storageItem = {
    cloudStorageOptions: {
      fileSet: {url: `gs://${bucketName}/${fileName}`},
    },
  };

  // Construct REST request for creating an inspect job
  const request = {
    parent: dlp.projectPath(projectId),
    inspectJob: {
      inspectConfig: {
        infoTypes: infoTypes,
        minLikelihood: minLikelihood,
        limits: {
          maxFindingsPerRequest: maxFindings,
        },
      },
      storageConfig: storageItem,
      actions: [
        {
          pubSub: {
            topic: `projects/${projectId}/topics/${topicId}`,
          },
        },
      ],
    },
  };

  // Verify the Cloud Pub/Sub topic and listen for job notifications via an
  // existing subscription.
  let subscription;
  pubsub.topic(topicId)
      .get()
      .then(topicResponse => {
        return topicResponse[0].subscription(subscriptionId);
      })
      .then(subscriptionResponse => {
        subscription = subscriptionResponse;
        // Create a DLP Cloud Storage File inspection job and wait for it to complete
        // (using promises)
        return dlp.createDlpJob(request);
      })
      .then(jobsResponse => {
        // Get the DLP job ID
        return jobsResponse[0].name;
      })
      .then(jobName => {
        // Watch the Cloud Pub/Sub topic until the DLP job completes processing file
        return new Promise((resolve, reject) => {
          const messageHandler = message => {
            if (message.attributes &&
                message.attributes.DlpJobName === jobName) {
              message.ack();
              subscription.removeListener('message', messageHandler);
              subscription.removeListener('error', errorHandler);
              resolve(jobName);
            } else {
              message.nack();
            }
          };

          const errorHandler = err => {
            subscription.removeListener('message', messageHandler);
            subscription.removeListener('error', errorHandler);
            reject(err);
          };

          subscription.on('message', messageHandler);
          subscription.on('error', errorHandler);
        });
      })
      .then(jobName => {
        // Wait for DLP job to fully complete
        return new Promise(resolve => setTimeout(resolve(jobName), 500));
      })
      .then(jobName => dlp.getDlpJob({name: jobName}))
      .then(wrappedJob => {
        const job = wrappedJob[0];
        console.log(`Job ${job.name} status: ${job.state}`);

        // set default destination to "sensitive" bucket
        var destBucketName = SENSITIVE_BUCKET;

        const infoTypeStats = job.inspectDetails.result.infoTypeStats;
        if (infoTypeStats.length > 0) {
          infoTypeStats.forEach(infoTypeStat => {
            console.log(
                `  Found ${infoTypeStat.count} instance(s)` +
                ` of infoType ${infoTypeStat.infoType.name}.`);
          });
        } else {
          // if no infotype match set destination to "nonsensitive" bucket
          destBucketName = NONSENSITIVE_BUCKET;
          console.log('No Matching infoType.');
        }
        // set destination to target bucket
        const destBucket = storage.bucket(destBucketName);
        // Move file to appropriate bucket
        // NOTE: No atomic "move" option exists in GCS, so this may fail to
        // delete the quarantined file
        return storage.bucket(bucketName).file(fileName).move(destBucket);
      })
      .then (() => {done()})
      .catch((err) => {
        if (err.message.toLowerCase().indexOf('not found') > -1) {
          console.error('[Fail] Error in inspectGCSFile:' + err);
          done();
        } else {
          console.error('[Retry] Error in inspectGCSFile:' + err);
          done(err);
        }
      });
}
