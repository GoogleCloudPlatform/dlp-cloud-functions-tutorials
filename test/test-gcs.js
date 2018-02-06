/**
 * Copyright 2017, Google, Inc.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

const fs = require(`fs`);
const path = require(`path`);
const proxyquire = require(`proxyquire`).noCallThru();
const sinon = require(`sinon`);
const test = require(`ava`);

const filename = `s_sample.txt`;

function getSample () {
  const filePath = path.join(__dirname, `../${filename}`);
  const file = {
    createReadStream: () => fs.createReadStream(filePath, { encoding: `utf8` })
  };
  const bucket = {
    file: sinon.stub().returns(file)
  };
  const storage = {
    bucket: sinon.stub().returns(bucket)
  };
  const StorageMock = sinon.stub().returns(storage);

  return {
    program: proxyquire(`../`, {
      '@google-cloud/storage': StorageMock
    }),
    mocks: {
      Storage: StorageMock,
      storage: storage,
      bucket: bucket,
      file: file
    }
  };
}

test.serial(`Fails without a bucket`, (t) => {
  const expectedMsg = `Bucket not provided. Make sure you have a "bucket" property in your request`;

  t.throws(
    () => getSample().program.dlpQuarantineGCS({ data: { name: `file` } }),
    Error,
    expectedMsg
  );
});

test.serial(`Fails without a file`, (t) => {
  const expectedMsg = `Filename not provided. Make sure you have a "file" property in your request`;

  t.throws(
    () => getSample().program.dlpQuarantineGCS({ data: { bucket: `bucket` } }),
    Error,
    expectedMsg
  );
});

