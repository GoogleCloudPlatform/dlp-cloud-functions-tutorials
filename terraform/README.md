
## Introduction

This folder provides terraform scripts to automate the creation of the resources and deployment of the Cloud Foundation code as described in [Automating the classification of data uploaded to Cloud Storage](https://cloud.google.com/architecture/automating-classification-of-data-uploaded-to-cloud-storage)


## Assumptions

The instructions assume you are running this from a cloud shell instance. 


## Contents

The following folders are available in the terraform folder of the repo:



* **Infra** - terraform script  that enables the required APIs, creates buckets, pub/sub topics & subscription.  Grants IAM roles to default app engine account   
* **dlp** -  terraform  script to grant required role to [DLP service agent](https://cloud.google.com/dlp/docs/iam-permissions#service_account). 
* **dlpfunction** - contains terraform to deploy cloud function
* **src** - empty folder that you will copy the function files to


## Deployment



1. Create the target project . If you wish to automate the creation of the project you can extend the terraform files here to include creation of the target  
2. Change folder to the infra folder 
3. Update the terraforms.tfvar file replacing the following with your own values

<table>
  <tr>
   <td>
Name
   </td>
   <td>description
   </td>
   <td>type
   </td>
  </tr>
  <tr>
   <td>YOUR_PROJECT_ID
   </td>
   <td>Project to be used for creating resources and deploying cloud function to
   </td>
   <td>string
   </td>
  </tr>
</table>




4. Deploy the resources defined in infra.tf

    terraform init


    terraform plan


    terraform apply 

5. Change folder to  ../dlp
6. Update the terraform.tfvar file  in this folder with YOUR_PROJECT_ID 
7. The [DLP service account is not created ](https://cloud.google.com/dlp/docs/iam-permissions?authuser=0#service_account) until at least one call is made to the DLP API. 

    To create the service account  update the curl command below by replacing YOUR_PROJECT_ID and then run the command 

        curl --request POST \
        "https://dlp.googleapis.com/v2/projects/YOUR_PROJECT_ID/locations/us-central1/content:inspect" \
             --header "X-Goog-User-Project: YOUR_PROJECT_ID" \
             --header "Authorization: Bearer $(gcloud auth print-access-token)" \
             --header 'Accept: application/json' \
             --header 'Content-Type: application/json' \
             --data '{"item":{"value":"google@google.com"}}' \
             --compressed

8. Deploy the resource defined in dlp.tf

    terraform init


    terraform plan


    terraform apply 

9.  Change folder to ../src
10. Copy the python code and requirements .txt file from ~/dlp-cloud-functions-tutorials/gcs-dlp-classification-python into this folder
11. Update the variables in the python.main file to reflect your values
12. Change folder to ../dlpfunction
13. Update the terraform.tfvar file in this folder with the value for YOUR_PROJECT_ID
14. Deploy the resource defined in dlp.tf

    terraform init


    terraform plan


    terraform apply 



## Production use guidance

The terraform scripts provided in this repo are to automate the creation of the resources and deployment of the Cloud Foundation code as described in  [Automating the classification of data uploaded to Cloud Storage](https://cloud.google.com/architecture/automating-classification-of-data-uploaded-to-cloud-storage) . They are not production ready.

To adapt for production the list below provides guidance:



* Create a custom service account with only the permissions required for the function to carry out its tasks. Use the custom service account  instead of the App Engine default service account . For guidance read [Function Identity](https://cloud.google.com/functions/docs/securing/function-identity).
* Update the declaration of the  variable names  of the buckets quarantine, sensitive and non sensitive buckets to reflect the project name ( similar to the function bucket name declaration) .
* Implement  tests.
    * Read [Testing Overview | Cloud Functions Documentation](https://cloud.google.com/functions/docs/testing/test-overview) for guidance on implementing tests for Cloud function code.
    * [https://www.hashicorp.com/blog/testing-hashicorp-terraform](https://www.hashicorp.com/blog/testing-hashicorp-terraform) provides a good overview of testing strategies for using Terraform.
* Read [Using Terraform with Google Cloud](https://cloud.google.com/docs/terraform).
* Update the terraform scripts in the infra and dlp folders to reflect your CI/CD processes for code and infrastructure.
    * Introduce  environment variables so that you can run the scripts in test, stage and  production environments.
    *  Configure [State: Remote Storage | Terraform by HashiCorp](https://www.terraform.io/language/state/remote) .	
    * For guidance on implementing a GitOps approach to managing your terraform managed Google cloud environment read [Managing infrastructure as code with Terraform, Cloud Build, and GitOps ](https://cloud.google.com/architecture/managing-infrastructure-as-code).
    * For guidance on implementing CI/CD for deployment to Cloud functions read [Deploying to Cloud Functions](https://cloud.google.com/build/docs/deploying-builds/deploy-functions).
* [Shift Security left](https://cloud.google.com/architecture/devops/devops-tech-shifting-left-on-security) and ensure best practices are followed to secure your software deployment pipeline.
* Follow best practices for your IaC pipelines.
* You can also create the target project as part of the infra configuration rather than creating it outside of terraform.