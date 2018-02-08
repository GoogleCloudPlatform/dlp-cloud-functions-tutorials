#!/bin/sh
#
# Copyright 2018, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless  required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

test_project="Your-test-project"
stage_bucket="your-quarantine-bucket"
sensitive_bucket="your-sensitive-data-bucket"
non_sensitive_bucket="your-nonsensitive-data-bucket"
sensitive_file="sample_s02.csv"
non_sensitive_file="sample_n01.txt"

export PROJECT_ID=$(gcloud config get-value project)

# Check test project set
if [ "$test_project" == "$PROJECT_ID" ];
    then
        echo Correct project set
    else
        echo Please set the correct project
        exit 1
fi

# Prepare test enviroment for a test run
gsutil rm gs://$stage_bucket/##
gsutil rm gs://$sensitive_bucket/##
gsutil rm gs://$non_sensitive_bucket/##

if [ -e $sensitive_file ];
    then
        echo Sample senstive file found
    else
        echo Sample sensitive file missing
        exit 1
fi

if [ -e $non_sensitive_file ];
    then
        echo Sample Non senstive file found
    else
        echo Sample Non sensitive file missing
    exit 1
fi

# Check buckets are empty
export check_empty_stage=$(gsutil ls gs://$stage_bucket/)
if [ "$check_empty_stage" != ""  ];
    then
        echo Stage bucket is not empty
        exit 1
    else
        echo No files found
fi

export check_empty_sensitive=$(gsutil ls gs://$sensitive_bucket/)
if [ "$check_empty_sensitive" != ""  ];
    then
        echo Sensitive bucket is not empty
        exit 1
    else
        echo No files found
fi

export check_empty_nonsensitive=$(gsutil ls gs://$non_sensitive_bucket/)
if [ "$check_empty_nonsensitive" != ""  ];
    then
        echo Non sensitive bucket is not empty
        exit 1
    else
        echo No files found
fi

# Upload test files
gsutil cp $non_sensitive_file $sensitive_file gs://$stage_bucket/

# Wait for function to execute
 sleep 30s

# Check files moved to correct bucket
export check_non_sensitive_file_exists=$(gsutil ls gs://$non_sensitive_bucket/$non_sensitive_file)
echo check_non_sensitive_file_exists =  $check_non_sensitive_file_exists
if [ "$check_non_sensitive_file_exists" != ""  ];
    then
        echo Non sensitive file moved to correct bucket
    else
        echo Non sensitive File not found when expected
        exit 1
fi

export check_sensitive_file_exists=$(gsutil ls gs://$sensitive_bucket/$sensitive_file)
if [ "$check_sensitive_file_exists" != ""  ];
    then
        echo Sensitive file moved to correct bucket
    else
        echo Sensitive File not found when expected
        exit 1
fi

# All checks passed
echo Test run completed succesfully
exit 0