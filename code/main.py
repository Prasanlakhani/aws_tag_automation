import json
import boto3
from datetime import datetime, timedelta
import secrets
import os
import shutil


#Initialized the AWS Service
s3_client = boto3.client('s3')
ec2_client = boto3.client('ec2')
sch_client = boto3.client('scheduler')


#Define Flag
flag_start = 'start'
flag_queued = 'queued'
flag_error = 'error'
flag_schedule = 'schedule'
flag_monitoring_off = 'monitoring_off'
flag_monitoring_on = 'monitoring_on'
flag_monitoring_done = 'Job_Completed'
flag_stop = 'stop'
    
# Checksum to protect for early execution
LIMIT_TIME = 2   # Time Limit in Minutes

#Define Variables
flag_counter=0


#Generate Unique Number
UID_Name=secrets.token_hex(3)
version = '1.0'
print(f"*******************************")
print(f"LAMDA function Started : {UID_Name} : Version : {version} ")


#Get Environment variables stored in lambda
#bucket_name = 'tag-test-prasan'
bucket_name = os.environ.get('s3storage')
lambda_name = os.environ.get('lambdaname')
region_name = os.environ.get('regionname')
iam_name = os.environ.get('iamrole')
acc_name = os.environ.get('account')
     
      
      
# Printing the variables stored in Lambda
print(f"bucket_name :  {bucket_name}")
print(f"lambda_name :  {lambda_name}")
print(f"region_name :  {region_name}")
print(f"iam_name :  {iam_name}")
print(f"acc_name :  {acc_name}")


s3_objects = s3_client.list_objects(Bucket=bucket_name)
print(f"s3_objects :  {s3_objects}")
keys = [obj['Key'] for obj in s3_objects['Contents']]
print(f"Number of Files :  {keys}")



def lambda_handler(event, context):


    for file_key_raw in keys:
        print(f"Current Working File :  {file_key_raw}")
              
#
        # Skip non-JSON files if needed
        if not file_key_raw.endswith('.json'):
            continue
            
        Main_function (file_key_raw)
#


        
   
    
def createSchedular (state, event_datetime,  UTC_event_datetime) :
    

    event_datetimeLocal = event_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    event_datetimeNameLocal = event_datetime.strftime("%Y%m%dT%H%M%S")
    
    
    event_datetimeUTC = UTC_event_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    
    print(f"*******************************")
    print(f"{state} : Local Time : {event_datetimeLocal} : UTC Time : {event_datetimeUTC} ")
    print(f"*******************************")    
    
    response_list_schedules = sch_client.list_schedules(State='ENABLED')
    schedules = response_list_schedules.get('Schedules', [])
    
    rule_name = f"{UID_Name}_{state}_{event_datetimeNameLocal}"
    print(f"rule_name which is going to be used : {rule_name}")

    if any(schedule.get('Name') == rule_name for schedule in schedules):

        response_get_schedule = sch_client.get_schedule(Name=rule_name)
        print(f"Rule Name already exist : {rule_name}")
        return_flag = 2
        return return_flag

    else : 
    
        print(f"Creating Schedule with Name : {rule_name}")
        
        try: 
            response = sch_client.create_schedule(
                #Description='Test Phase',
                FlexibleTimeWindow={
                    'Mode': 'OFF'
                },
                Name=rule_name,
                ScheduleExpression=f"at({event_datetimeUTC})",
                State='ENABLED',
                Target={
                    'RoleArn': f'arn:aws:iam::{acc_name}:role/{iam_name}',
                    'Arn': f'arn:aws:lambda:{region_name}:{acc_name}:function:{lambda_name}'
                }
            )
        
            print(f"Scheduled : {rule_name} created successfully.")
            print(f"*******************************") 
            return_flag = 0
            return return_flag
        except Exception as e:
            print(f"Error: {str(e)}")

 
def HostScheduledaction (hosts_ina, file_key1, data1,  event_status, event_datetime1, tag_key1, tag_indicator, flag_monitoring, STR_TIME_NOW31 ) : 


    print(f"Started : Flag Status : {event_status} : {event_datetime1}")

    CTIME = event_datetime1.strftime("%Y, %m, %d, %H, %M, %S")


    print(f"STR_TIME_NOW31 : {STR_TIME_NOW31}")

    PTIME =  event_datetime1 - STR_TIME_NOW31

    STIME = PTIME.total_seconds()
    FTIME = (int(STIME/60))
    print(f"Time Remaining : {FTIME}")

    if (LIMIT_TIME) >= (FTIME) :                                                                                                                        # ISSUES
        print(f"Starting the activity : ")
        print(f"hosts : {hosts_ina}")

        for instance_name in hosts_ina:
            print(f"Entered for loop : ")
            response = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}])                       
            print(f"response : {response}")

            current_tags = response['Reservations'][0]['Instances'][0].get('Tags', [])
            print(f"current_tags associated : {current_tags}")

            instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']

            print(f"instance_id : {instance_id}")
    

            for tag in current_tags:
                print(f"tag : {tag}")
                if tag['Key'] == tag_key1 :
                    if tag['Value'] == tag_indicator :
                        print(f"{instance_id} current status is already  {tag_key1} : {tag_indicator}")
                    else : 
                        print(f"Changing monitoring tag for instance {instance_id} to {tag_indicator}")
                        ec2_client.create_tags(Resources=[instance_id], Tags=[{'Key': tag_key1, 'Value': tag_indicator}])
                        print(f"Changed monitoring tag for instance {instance_id} to {tag_indicator}")
                        data1['Flag'] = flag_monitoring
                        data1['Comments'] = 'Activity inprogress , Please dont change the file'
                        modified_json = json.dumps(data1)
                        s3_client.put_object(Body=modified_json, Bucket=bucket_name, Key=file_key1)
                        break
                else:
                    print(f"Monitoring tag not found for instance {instance_id}")
    
    else : 
        print("Change Window not yet started.")

    return


   
def Precheck (file_key1, data1, hosts_in, event_datetime_start1, event_datetime_stop1, event_datetime_cleaup1, UTC_event_datetime_start1, UTC_event_datetime_stop1, UTC_event_datetime_cleanup1, tag_key1, STR_TIME_NOW31 ) : 
    flag_precheck = 0

    for instance_name in hosts_in:
        response = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}])                       
        current_tags = response['Reservations'][0]['Instances'][0].get('Tags', [])
        instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']

        print(f"Checking instance_name : {instance_name} : instance_id : {instance_id} for Tags")
    
        # Find the monitoring tag and toggle its value
        for tag in current_tags:
            print(f"tag : {tag}")
            if tag['Key'] == tag_key1:
                flag_precheck = 0
                print(f"Tag Found")
                break
            else:
                flag_precheck = 1
                print(f"Monitoring tag not found for instance {instance_id}")
            
        if flag_precheck == 0 : 
            continue
        else : 
            if flag_precheck == 1 : 
                break
                    

                
    
    CTIME = event_datetime_start1.strftime("%Y, %m, %d, %H, %M, %S")
    ETIME = event_datetime_stop1.strftime("%Y, %m, %d, %H, %M, %S")
    
    print(f"event_datetime_start : {event_datetime_start1}")               # Delete
    print(f"event_datetime_stop : {event_datetime_stop1}")               # Delete


    PTIME = event_datetime_start1 - STR_TIME_NOW31
    PETIME = event_datetime_stop1 - event_datetime_start1
    STIME = PTIME.total_seconds()
    FTIME = (int(STIME/60))
    SETIME = PETIME.total_seconds()
    FETIME = (int(SETIME/60))
    ZERO_TIME = 0
    
    if flag_precheck == 1 :
        print(f"flag_precheck : {flag_precheck}  ")            
        Error (file_key1, data1,'ATTENTION : Not all host has the necessary tag, Please check ')
        
    else : 
        if (ZERO_TIME) < (FTIME):
            flag_precheck = 0
            print(f"Start Date Looks Good ")               # Delete
        else : 
            flag_precheck = 2
            

    if flag_precheck == 2 :
        Error (file_key1, data1,'ATTENTION : The Scheduled start date/time is before current time ')
    else :
        if flag_precheck == 1 :
            print(f"Error Stop   ")
        else : 
            if (ZERO_TIME) < (FETIME) :
                flag_precheck = 0
                print(f"Stop Date Looks Good ")              # Delete
            else : 
                Error (file_key1, data1,'ATTENTION : The Scheduled stop date/time is before start date/time time ')
                # Delete
        

                
    if flag_precheck == 0 :
        Flag_Status = flag_queued
        print(f"Flag_Status : {Flag_Status}")
        
        flag_queued_state = createSchedular ("Start", event_datetime_start1, UTC_event_datetime_start1)
        flag_queued_state = createSchedular ("Stop", event_datetime_stop1, UTC_event_datetime_stop1)
        flag_queued_state = createSchedular ("Cleanup", event_datetime_cleaup1, UTC_event_datetime_cleanup1)
        
        if flag_queued_state == 0 :
            print(f"flag_queued_state : {flag_queued_state}  ")
            data1['Flag'] = flag_schedule
            data1['UID'] = UID_Name
            data1['Comments'] = 'Pre Check, Completed, Waiting for activity to start'
            
            
            modified_json = json.dumps(data1)
                     
            s3_client.put_object(Body=modified_json, Bucket=bucket_name, Key=file_key1)
            print(f"Completed : {flag_schedule} : UID_Name : {UID_Name} ")
        else :
            if flag_queued_state == 2 :
                 print(f"Rule Name already exist ")
            else :
                Error (file_key1,data1, 'ATTENTION : Issue while scheduling the job, please check. ')
            

def cleanup (state, event_datetime, Json_UID1) : 
    event_datetimeNameLocal = event_datetime.strftime("%Y%m%dT%H%M%S")
    
    response_list_schedules = sch_client.list_schedules(State='ENABLED')
    schedules = response_list_schedules.get('Schedules', [])
    
    rule_name = f"{Json_UID1}_{state}_{event_datetimeNameLocal}"
    print(f"rule_name : {rule_name}")
    
    if any(schedule.get('Name') == rule_name for schedule in schedules):
        response = sch_client.delete_schedule(Name=rule_name)
        print(f"Scheduled : {rule_name} deleted successfully.")
        return_flag = 0
        
    else : 
        print(f"Scheduled job doesnt exist : {rule_name}")
        return_flag = 1
        
    return return_flag
    
    


    
            
def Error (file_key1, data1, Error_Comments) : 
    data1['Flag'] = flag_error
    print(f"ERROR : {Error_Comments}")
    data1['Comments'] = Error_Comments
    modified_json = json.dumps(data1)
    s3_client.put_object(Body=modified_json, Bucket=bucket_name, Key=file_key1)
    print(f"Upload Completed : {flag_error}  ")

    
    
def Main_function (file_key) :
    try:
#       # Read the JSON file content
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        data = json.loads(response['Body'].read().decode('utf-8'))

        # Process the JSON data as needed
        print(f"Processing : {file_key} : It load : {data}")
        
        
        ####FETCH Variables from the File#########################
        Flag_Status = data.get('Flag')
        
        event_date_start = data.get('Event_Start_date')
        event_time_start = data.get('Event_Start_time')
        event_date_stop = data.get('Event_Stop_date')
        event_time_stop = data.get('Event_Stop_time')
        
        timezone = data.get('Timezone_UTC')
        
        timezone_variable = data.get('timezone_Test', 'UTC')
        timezone_hours, timezone_minutes = map(int, timezone.split(':'))
        time_difference = timedelta(hours=timezone_hours, minutes=timezone_minutes)
        
        tag_key = data.get('Tag')
        tag_value_start = data.get('Tag_On')
        tag_value_stop = data.get('Tag_Off')
        Json_Name = data.get('Name')                # Optional
        Json_UID = data.get('UID')                 # Will be Updated
        Json_Comments = data.get('Comments')  
        
        # Fetch Host Info
        hosts = data.get('Hosts', [])
        
        
        
        # Define Start / Stop / Cleanup time
        event_datetime_start = datetime.strptime(f"{event_date_start} {event_time_start}", "%Y-%m-%d %H:%M:%S")
        event_datetime_cleaup = event_datetime_stop = datetime.strptime(f"{event_date_stop} {event_time_stop}", "%Y-%m-%d %H:%M:%S")
        event_datetime_cleaup += timedelta(hours=1)
        
        # Fetch Current Time & Do UTC Calculation
        TIME_NOW = datetime.now()
        UTC_Time = TIME_NOW + time_difference
        
        UTC_event_datetime_start = event_datetime_start - time_difference
        UTC_event_datetime_stop = event_datetime_stop - time_difference
        UTC_event_datetime_cleanup = event_datetime_cleaup - time_difference
        
        print(f"*******************************")                
        print(f"*******************************")
        print(f"event_datetime_start : {event_datetime_start}")
        print(f"event_datetime_stop : {event_datetime_stop}")
        print(f"event_datetime_cleaup : {event_datetime_cleaup}")
        print(f"*******************************")
        print(f"UTC_event_datetime_start : {UTC_event_datetime_start}")
        print(f"UTC_event_datetime_stop : {UTC_event_datetime_stop}")
        print(f"UTC_event_datetime_cleanup : {UTC_event_datetime_cleanup}")                        
        print(f"*******************************")            
        print(f"*******************************")               
        
        STR_TIME_NOW = UTC_Time.strftime("%Y%m%d%H%M%S")
        STR_TIME_NOW2 = UTC_Time.strftime("%Y-%m-%d %H:%M:%S") 
        STR_TIME_NOW3 = datetime.strptime(STR_TIME_NOW2, "%Y-%m-%d %H:%M:%S")

        print(f"UTC : {timezone} : {UTC_Time}")
  


        try:
        
            if Flag_Status == flag_start :
                
                print(f"Flag_Status : {Flag_Status}")
                Precheck (file_key, data, hosts, event_datetime_start, event_datetime_stop, event_datetime_cleaup, UTC_event_datetime_start, UTC_event_datetime_stop, UTC_event_datetime_cleanup, tag_key, STR_TIME_NOW3)
                
            # During maintenece Window Start
            if Flag_Status == flag_schedule :
                
        
                print(f"Flag_Status : {Flag_Status}")
                HostScheduledaction (hosts, file_key, data, Flag_Status, event_datetime_start, tag_key , tag_value_stop, flag_monitoring_off, STR_TIME_NOW3)
            
            # During maintenece Window Finish
            if Flag_Status == flag_monitoring_off :
            
                print(f"Flag_Status : {Flag_Status}")
                HostScheduledaction (hosts, file_key, data, Flag_Status, event_datetime_stop, tag_key, tag_value_start, flag_monitoring_on, STR_TIME_NOW3)
        
            if Flag_Status == flag_monitoring_on :
                
                print(f"Flag_Status : {Flag_Status}")
                
                returnresponse = cleanup ("Start", event_datetime_start, Json_UID) 
                returnresponse = cleanup ("Stop", event_datetime_stop,Json_UID)
                returnresponse = cleanup ("Cleanup", event_datetime_cleaup,Json_UID)
                
                if returnresponse == 0 : 
                    print(f"CleanUp Done : Deleting the file : {Flag_Status}")
                    response = s3_client.delete_object(Bucket=bucket_name,Key=file_key)
                    print(f"Done")

                else :
                    print(f"Check manually & delete all the schedules : {Flag_Status}")
        
            if Flag_Status == flag_stop :
                
                print(f"Flag : {Flag_Status}")
        
                returnresponse = cleanup ("Start", event_datetime_start, Json_UID) 
                returnresponse = cleanup ("Stop", event_datetime_stop, Json_UID)
                returnresponse = cleanup ("Cleanup", event_datetime_cleaup, Json_UID)
                
                            
                if returnresponse == 0 : 
                    data['Flag'] = flag_monitoring_done
                    data['Comments'] = 'The Cleanup is Sucessfully after you stopped the activity'
                    modified_json = json.dumps(data)
                    s3_client.put_object(Body=modified_json, Bucket=bucket_name, Key=file_key)  

        except Exception as e:
            print(f"Error: {str(e)}")                        

    except Exception as e:
        print(f"Error processing {file_key}: {e}")
#       
    return {
        'statusCode': 200,
            'body': 'Function executed successfully!'
    }
