import os
import boto3
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, redirect, send_file, url_for,jsonify
from ec2_metadata import ec2_metadata
from s3_demo import list_files, download_file, upload_file
from typing import List, Dict
import mysql.connector
import json
from os import environ
from sqs_demo import send_message, receive_message, delete_message




def sensor():
    response=receive_message(queuename=environ['QUEUE_NAME'])
    # print(len(response.get('Messages', [])))
    if len(response.get('Messages', [])) > 0:
        for message in response.get("Messages", []):
            message_body = message["Body"]
            message_handle = message['ReceiptHandle']
        client = boto3.client('sns', region_name='eu-central-1')
        sendMessage = client.publish(
            TargetArn=environ['ARN'],
            Message=message_body,
            Subject='Message from sqs',
        )
        delete_message(receipt_handle=message_handle,queuename=environ['QUEUE_NAME'])



sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'interval',seconds=15)
sched.start()

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = environ['S3_BUCKET']
def getMysqlConnection():
    return mysql.connector.connect(user=environ['MYSQL_USER'], host=environ['MYSQL_HOST'], port='3306', password=environ['MYSQL_PASSWORD'], database='images')
# app.config['MYSQL_HOST'] = environ['MYSQL_HOST']
# app.config['MYSQL_USER'] = environ['MYSQL_USER']
# app.config['MYSQL_PASSWORD'] = environ['MYSQL_PASSWORD']
# app.config['MYSQL_DB'] = 'test'



@app.route('/')
def hello_world():
    region=ec2_metadata.region
    az=ec2_metadata.availability_zone
    return render_template('index.html', az=az, region=region)

@app.route('/list')
def get_images():
    db = getMysqlConnection()
    print(db)
    try:
        sqlstr = "SELECT * from images"
        cur = db.cursor()
        cur.execute(sqlstr)
        images = cur.fetchall()
    except Exception as e:
        print("Error in SQL:\n", e)
    finally:
        db.close()
    return render_template('list.html', contents=images, bucket=BUCKET)

@app.route('/random')
def get_random():
    db = getMysqlConnection()
    print(db)
    try:
        sqlstr = "SELECT * FROM images ORDER BY RAND() LIMIT 1"
        cur = db.cursor()
        cur.execute(sqlstr)
        images = cur.fetchall()
    except Exception as e:
        print("Error in SQL:\n", e)
    finally:
        db.close()
    return render_template('list.html', contents=images, bucket=BUCKET)

@app.route('/storage')
def storage():
    contents = list_files(BUCKET)
    db = getMysqlConnection()
    print(db)
    try:
        sqlstr = "SELECT * FROM images"
        print(sqlstr)
        cur = db.cursor()
        cur.execute(sqlstr)
        images = cur.fetchall()
    except Exception as e:
        print("Error in SQL:\n", e)
    finally:
        db.close()
    return render_template('storage.html', contents=images, bucket=BUCKET)



@app.route('/upload', methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(f.filename)
        upload_file(f"{f.filename}", BUCKET)
        s3_client = boto3.client('s3')
        k = s3_client.head_object(Bucket=BUCKET, Key=f.filename)

        db = getMysqlConnection()
        try:
            sqlstr = """INSERT INTO images
                     (name, date, size, ext) 
                     VALUES(%s,%s,%s,%s)"""

            print(sqlstr)
            params = (f.filename, k['LastModified'].strftime("%Y-%m-%d %H:%M:%S"), k['ContentLength'], os.path.splitext(f.filename)[1][1:])
            print(params)
            cur = db.cursor()
            cur.execute(sqlstr, params)
            db.commit()
        except Exception as e:
            print("Error in SQL:\n", e)
        finally:
            db.close()

        message = 'Тhe image was loaded with the following parameters:\nName: ' + f.filename 
        message += ',\nLast update: '+ k['LastModified'].strftime("%Y-%m-%d %H:%M:%S")
        message += ',\nSize: '+ str(k['ContentLength']) + ' bytes,\nExtesion: '+ os.path.splitext(f.filename)[1][1:]+ '.\n'
        message += 'Link to download: https://'+ BUCKET + '.s3.eu-central-1.amazonaws.com/'+ f.filename 
        print(message)

        send_message(message=message,queuename=environ['QUEUE_NAME'])

        return redirect("/storage")


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    if request.method == 'GET':
        output = download_file(filename, BUCKET)

        return send_file(output, as_attachment=True)


@app.route('/subscribe')
def subscribe():
    client = boto3.client(
        "sns",
        region_name='eu-central-1'
    )   
    topic_arn = os.environ['ARN']  

# Add SMS Subscribers
    responce = client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint='ausard@yandex.ru',
        ReturnSubscriptionArn=True 
    )
    print(responce['SubscriptionArn'])
    os.environ['SUBCRIPTIONARN'] = responce['SubscriptionArn'] 
    return render_template('subscribe.html', subscribe=True, topic=topic_arn)

@app.route('/unsubscribe')
def unsubscribe():
    client = boto3.client(
        "sns",
        region_name='eu-central-1'
    )   

    print(os.environ['SUBCRIPTIONARN'])
    responce = client.unsubscribe(
        SubscriptionArn =  os.environ['SUBCRIPTIONARN']
    )
    return render_template('subscribe.html', subscribe=False, topic=os.environ['SUBCRIPTIONARN'])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)