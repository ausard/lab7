import os
import boto3

from flask import Flask, render_template, request, redirect, send_file, url_for,jsonify
from ec2_metadata import ec2_metadata
from s3_demo import list_files, download_file, upload_file
from typing import List, Dict
import mysql.connector
import json
from os import environ



app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = environ['S3_BUCKET']

# app.config['MYSQL_HOST'] = environ['MYSQL_HOST']
# app.config['MYSQL_USER'] = environ['MYSQL_USER']
# app.config['MYSQL_PASSWORD'] = environ['MYSQL_PASSWORD']
# app.config['MYSQL_DB'] = 'test'

def getMysqlConnection():
    return mysql.connector.connect(user=environ['MYSQL_USER'], host=environ['MYSQL_HOST'], port='3306', password=environ['MYSQL_PASSWORD'], database='images')


@app.route('/')
def hello_world():
    region=ec2_metadata.region
    az=ec2_metadata.availability_zone
    return render_template('index.html', az=az, region=region)


# @app.route('/list')
# def list():
#     cursor = mysql.connection.cursor() 
#     #execute select statement to fetch data to be displayed in combo/dropdown
#     cursor.execute('SELECT firstName,lastName FROM MyUsers') 
#     #fetch all rows ans store as a set of tuples 
#     joblist = cursor.fetchall() 
#     cursor.close()
#     #render template and send the set of tuples to the HTML file for displaying
#     return render_template("input.html",joblist=joblist )

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

        print(k['ContentLength'])
        print(k['LastModified'])
        print(k['ContentType'])
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
        return redirect("/storage")


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    if request.method == 'GET':
        output = download_file(filename, BUCKET)

        return send_file(output, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)