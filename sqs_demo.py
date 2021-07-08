import boto3

def get_queue_url(queuename):
    sqs_client = boto3.client("sqs", region_name='eu-central-1')
    response = sqs_client.get_queue_url(
        QueueName=queuename,
    )
    return response["QueueUrl"]

def send_message(message, queuename):
    sqs = boto3.resource('sqs', region_name='eu-central-1')
    queue = sqs.get_queue_by_name(QueueName=queuename)
    response = queue.send_message(MessageBody=message)
    print(response)

def receive_message(queuename):
    sqs = boto3.client('sqs', region_name='eu-central-1')
    response = sqs.receive_message(
        QueueUrl=get_queue_url(queuename),
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )

    # print(f"Number of messages received: {len(response.get('Messages', []))}")

    # for message in response.get("Messages", []):
    #     message_body = message["Body"]
    #     print(f"Message body: {message_body}")
    #     print(f"Receipt Handle: {message['ReceiptHandle']}")
    return response

def delete_message(receipt_handle,queuename):
    sqs_client = boto3.client("sqs", region_name="eu-central-1")
    response = sqs_client.delete_message(
        QueueUrl=get_queue_url(queuename),
        ReceiptHandle=receipt_handle,
    )
    print(response)