# github-action-aws-secrets-sync
Synchronizes github secrets into AWS Secrets Manager.

## Setup 
Set the following environmental variables for the custom action:
* AWS_ACCESS_KEY_ID: AWS standard auth env variable
* AWS_SECRET_ACCESS_KEY: AWS standard auth env variable
* AWS_DEFAULT_REGION: AWS Region where the AWS Secret's entry is located
* AWS_TGT_SECRETS_ARN: AWS Secrets ARN where the github secrets will be stored into
* SECRETS_CONFIG_FILE: filename where the secrets are stored. A previous action step will be needed to properly store the secrets into the file and make it accesible for this custom action. For example:
  * `echo '${{ toJson(secrets) }}' > ${{ env.GITHUB_WORKSPACE }}/${{ env.SECRETS_CONFIG_FILE }})`
* EXCLUDE_FILTER: (OPTIONAL). Comma separated string. The secrets with the matching pattern will be excluded from the synchronization into AWS Secrets Manager. Useful when wanting to exclude internal secrets used for CI related tasks.
  * Example: using "INTERNAL_" as pattern, will exclude the key "INTERNAL_AWS_ACCESS_KEY_ID" from the sync up.
* INCLUDE_FILTER: (OPTIONAL). Comma separated string. Only the secrets with the matching patterns will be synced into AWS Secrets Manager. Useful when multiple environment properties are stored into the same github repository and need to be synced into different AWS Secrets entries.
  * Example: using "STAGING_" as pattern, will include the key "STAGING_DB_URL" and exclude the key "LIVE_DB_URL" from the sync up.
* REMOVE_PATTERN: (OPTIONAL). Comma separated string. Remove the pattern from the key to be synced into AWS Secrets Manager. 
  * Example: using "STAGING_" as pattern, will make the key "STAGING_DB_URL" to be stored as "DB_URL"

## Local testing

Use `act` tool for github action's local testing.
Example invocation:
`act --secret-file .github/workflows/.secrets -W ./.github/workflows/local_test_custom_action.yaml workflow_dispatch`