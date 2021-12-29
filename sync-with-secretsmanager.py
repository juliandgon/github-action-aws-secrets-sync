
import os
import logging
import json,yaml,re
import argparse
import traceback,sys
from boto3 import Session

def setLogger():
    # Setting logging level
    loglevel = os.getenv("LOGLEVEL","INFO")
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)

# Script used for updating AWS secrets entries with the values contained in json config files
def init_aws_session():
    # Create a Secrets Manager client
    session = Session()
    client = session.client(
        service_name='secretsmanager'
    )
    return client


def update_secret(secret_arn, jsonString,DryRun=False):
    client = init_aws_session()
    if DryRun:
        logging.info(f"(dryrun) Updating secret entry: {secret_arn}")
        logging.debug(f"(dryrun) Content file: {jsonString}")
        return 0
    logging.info(f"Updating secret entry: {secret_arn}")
    logging.debug(f"Content file: {jsonString}")
    try:
        client.update_secret(SecretId=secret_arn, SecretString=jsonString)
    
    except Exception as e:
        logging.error(f"{traceback.format_exception(*sys.exc_info())} ")
        return 1
    return 0


def get_secret(secret_name):
    client = init_aws_session()

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    
    return json.loads(secret)

def sync_secrets(secret_arn,secret_file,include_filter,exclude_filter,remove_pattern,dry_run=False):
    # Get the Json content from the file with the secrets to be synced
    with open(secret_file) as parsingFile:    
        try: 
            newValues = yaml.load(parsingFile, yaml.SafeLoader) # Load through YAML for safe loading
        except yaml.parser.ParserError as error:
            logging.info(f"failed to parse json, assuming an almost json... trying custom parsing")
            with open(secret_file) as parsingFile:    
                jsonfile = parsingFile.read()
            jsonCorrected = re.sub(r"([\t\s]*)(.*):\s([^,\n]*)(,?)", r'\1"\2": "\3"\4', jsonfile)
            newValues = json.loads(jsonCorrected) # Load through YAML for safe loading
        
        
        # If a include filter parameter was used, only get the matching secrets for syncing
        if include_filter:
            check_value_in_list = lambda x: any([f in x[0] for f in include_filter])
            newValues = dict(filter(check_value_in_list , newValues.items()))
            
        # If a exclude filter parameter was used, remove matching secrets for syncing
        if exclude_filter:
            check_value_not_in_list = lambda x: not any([f in x[0] for f in exclude_filter])
            newValues = dict(filter(check_value_not_in_list , newValues.items()))
            
        if remove_pattern:
            jsonDataFilter = {}
            for patternToRemove in remove_pattern:
                for key in newValues:
                    keyModified = key.replace(patternToRemove, '')
                    jsonDataFilter[keyModified] = newValues[key]
                                
            newValues = jsonDataFilter

        oldValues = get_secret(secret_arn)
        oldValues.update(newValues)
        
        jsonString = json.dumps(oldValues)


    result = update_secret(secret_arn=secret_arn,jsonString=jsonString,DryRun=dry_run)
    if result > 0:
        logging.error(f"ERROR. Could not update secret manager entry")
        exit(result)

    logging.info(f"AWS Secret Manager entry synced succesfully!")
    return 0

if __name__=='__main__':
    setLogger()
    parser = argparse.ArgumentParser("sync-with-secretsmanager")
    parser.add_argument('--secret_arn',required=True, nargs='?', help='AWS secret manager ARN  help')
    parser.add_argument('--secret_json_file',required=True, nargs='?', help='secret json file help')
    parser.add_argument('--include_filter_match', type=str, nargs='?', help='Include only filter for matching sequence')
    parser.add_argument('--exclude_filter_match', type=str, nargs='?', help='Exclude filter for matching sequence')
    parser.add_argument('--remove_pattern', type=str, nargs='?', help='Remove matching pattern in keys values')
    parser.add_argument('--dryrun', nargs='?', help='Dry run')
    args = parser.parse_args()
    secretARN=args.secret_arn
    secretsJsonFile=args.secret_json_file
    include_filter=args.include_filter_match
    include_filter = list(filter(None,[s.strip() for s in include_filter.split(",")]))
    exclude_filter=args.exclude_filter_match
    exclude_filter = list(filter(None, [s.strip() for s in exclude_filter.split(",")]))
    remove_pattern=args.remove_pattern
    remove_pattern = list(filter(None, [s.strip() for s in remove_pattern.split(",")]))
    _dryRun=args.dryrun

    rc = sync_secrets(secret_arn=secretARN,secret_file=secretsJsonFile,include_filter=include_filter,exclude_filter=exclude_filter,remove_pattern=remove_pattern,dry_run=_dryRun)
    exit(rc)
