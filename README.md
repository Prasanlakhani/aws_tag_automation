# aws_tag_automation
This aws lamda will disable &amp; re enable the tag at scheduled time, provided as Json file

## Tag Automation

Tag Automation is a tool designed to automate tagging operations based on JSON configurations. Users can upload a JSON file to an S3 bucket, triggering a Lambda function. This Lambda function, in turn, creates schedulers based on the specified start and stop times in the JSON file. Cleanup schedulers are also created to delete all the scheduled events one hour after activity is comepleted.

## JSON Configuration Example

```json
{
  "Version": "1.0",
  "Name": "A517965",
  "UID": "778feb",
  "Tag": "Eviden_Manage",
  "Tag_On": "true1",
  "Tag_Off": "false1",
  "Timezone_UTC": "+5:30",
  "Event_Start_date": "2024-01-05",
  "Event_Start_time": "17:00:00",
  "Event_Stop_date": "2024-01-05",
  "Event_Stop_time": "17:30:00",
  "Flag": "start",
  "Region": "your-region",
  "Comments": "XXXX",
  "Hosts": ["Test"]
}

```

## Getting Started
To use Tag Automation, follow these steps:

Define Variables: Declare variables in the variables.tf file, which will be used for Lambda function execution. Variables include:

- s3storage: S3 bucket to store the JSON file. #Should be Unique
- lambdaname: Lambda function name.
- iamrole: IAM role name.
- regionname: AWS region for deployment.
- account: AWS account ID.
Upload JSON Configuration: Upload the JSON configuration file to the specified S3 bucket.

Trigger Lambda Function: Lambda function is triggered automatically by S3 upload.

Scheduler Creation: The Lambda function creates schedulers based on the JSON configuration.

Cleanup Schedulers: Cleanup schedulers are created to delete all scheduled events one hour after the specified stop time.

## Variables in Lambda Function which needs to be declared if deploying manually
- s3storage: S3 bucket to store the JSON file.
- lambdaname: Lambda function name.
- iamrole: IAM role name.
- regionname: AWS region for deployment.
- account: AWS account ID.

