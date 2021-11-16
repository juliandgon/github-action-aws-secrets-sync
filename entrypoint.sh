#!/bin/bash
#set -e

[[ -z "${AWS_TGT_SECRETS_ARN+x}" ]] && echo "ERROR. Missing required environment variable AWS_TGT_SECRETS_ARN" && exit 1
[[ -z "${SECRETS_CONFIG_FILE+x}" ]] && echo "ERROR. Missing required environment variable SECRETS_CONFIG_FILE" && exit 1


#aws secretsmanager update-secret --secret-id ${TGT_AWS_SECRETS_ARN} --secret-string file://${SECRETS_CONFIG_FILE}
python3 ${SCRIPT_DIR}sync-with-secretsmanager.py --secret_arn ${AWS_TGT_SECRETS_ARN} --secret_json_file ${SECRETS_CONFIG_FILE} --prefix_filter="${FILTER_PREFIX}"

