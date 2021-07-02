import os

from flask import Flask, render_template, request, redirect, send_file, url_for
from ec2_metadata import ec2_metadata
from s3_demo import list_files, download_file, upload_file
from flask_mysqldb import MySQL
from os import environ


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = environ['S3_BUCKET']
# BUCKET ="aliakseisabetskiaws"

app.config['MYSQL_HOST'] = environ['MYSQL_HOST']
app.config['MYSQL_USER'] = environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = 'test'
mysql = MySQL(app)


@app.route('/')
def hello_world():
    region="ec2_metadata.region"
    az="ec2_metadata.availability_zone"
    return render_template('index.html', az=az, region=region)

# @app.route('/insert', methods=['GET', 'POST'])
# def index():
#     if request.method == "POST":
#         details = request.form
#         firstName = details['fname']
#         lastName = details['lname']
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO MyUsers(firstName, lastName) VALUES (%s, %s)", (firstName, lastName))
#         mysql.connection.commit()
#         cur.close()
#         return 'success'
#     return render_template('index.html')

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