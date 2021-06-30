import os

from flask import Flask, render_template, request, redirect, send_file, url_for
from ec2_metadata import ec2_metadata
from s3_demo import list_files, download_file, upload_file
from flask_mysqldb import MySQL
from os import environ


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = "aliakseisabetskiaws"

# MYSQL_USER=environ['MYSQL_USER']
# MYSQL_PASSWORD=environ['MYSQL_PASSWORD']
# MYSQL_HOST=environ['MYSQL_HOST']
# # MYSQL_DATABASE=environ['MYSQL_DATABASE']
# MYSQL_DATABASE="test"
app.config['MYSQL_HOST'] = environ['MYSQL_HOST']
app.config['MYSQL_USER'] = environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = 'test'
mysql = MySQL(app)


@app.route('/')
def hello_world():
    region=ec2_metadata.region
    az=ec2_metadata.availability_zone
    res = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>title</title></head>"
    res+="<body><div>Region: " + region + "</div>"
    res+="<div>Avialability zone: " + az + "</div>"
    res+="<a href=/storage>storage</a>"
    res+="</body></html>"  
    return res

@app.route('/insert', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        details = request.form
        firstName = details['fname']
        lastName = details['lname']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO MyUsers(firstName, lastName) VALUES (%s, %s)", (firstName, lastName))
        mysql.connection.commit()
        cur.close()
        return 'success'
    return render_template('index.html')



@app.route('/storage')
def storage():
    contents = list_files(BUCKET)
    return render_template('storage.html', contents=contents)


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(f.filename)
        upload_file(f"{f.filename}", BUCKET)

        return redirect("/storage")


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    if request.method == 'GET':
        output = download_file(filename, BUCKET)

        return send_file(output, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)