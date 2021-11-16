# github-action-aws-secrets-sync
Synchronizes github secrets into AWS Secrets Manager.

## Setup 
Set the following environmental variables for the custom action:
* AWS_ACCESS_KEY_ID: AWS standard auth env variable
* AWS_SECRET_ACCESS_KEY: AWS standard auth env variable
* AWS_DEFAULT_REGION: AWS Region where the AWS Secret's entry is located
* AWS_TGT_SECRETS_ARN: AWS Secrets ARN where the github secrets will be stored into
* SECRETS_CONFIG_FILE: filename where the secrets are stored. A previous action step will be needed to properly store the secrets into the file and make it accesible for this custom action. For example:
  * `echo "${{ toJson(secrets) }}" > ${{ env.GITHUB_WORKSPACE }}/${{ env.SECRETS_CONFIG_FILE }})`
* FILTER_PREFIX: (OPTIONAL). Only the secrets with the matching prefix will be synced into AWS Secrets Manager. Useful when multiple environment properties are stored into the same github repository and need to be synced into different AWS Secrets entries.

## Local testing

Use `act` tool for github action's local testing.