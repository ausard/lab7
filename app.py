import os

from flask import Flask, render_template, request, redirect, send_file, url_for
from ec2_metadata import ec2_metadata
from s3_demo import list_files, download_file, upload_file
from flask_sqlalchemy import SQLAlchemy 
from os import environ


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = "aliakseisabetskiaws"

MYSQL_USER=environ['MYSQL_USER']
MYSQL_PASSWORD=environ['MYSQL_PASS']
MYSQL_HOST=environ['MYSQL_HOST']
# MYSQL_DATABASE=environ['MYSQL_DATABASE']
MYSQL_DATABASE="test"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{user}:{passwd}@{host}/{db}'.format(user=MYSQL_USER, passwd=MYSQL_PASSWORD, host=MYSQL_HOST, db=MYSQL_DATABASE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # instantiate database object #interface with flask app itself

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    comment = db.Column(db.String(1000))

@app.route('/')
def hello_world():
    region=ec2_metadata.region
    az=ec2_metadata.availability_zone
    res = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>title</title></head>"
    res+="<body><div>Region: " + region + "</div>"
    res+="<div>Avialability zone: " + az + "</div>"
    res+="</body></html>"  
    return res
@app.route('/all')
def all():
    result = Comments.query.all() # use the comments class
    #result = Comments.query.filter_by(name='Ruan')
    counts = Comments.query.count()
    return render_template('index.html', result=result, counts=counts)

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,age))
        mysql.connection.commit()
        cursor.close()
        return f"Done!!"

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

@app.route('/sign')
def sign():
    return render_template('sign.html')

@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/process', methods=['POST'])
def process():
    name = request.form['name']
    comment = request.form['comment']

    signature = Comments(name=name, comment=comment)      # instantiate an object. signature object, from comments class
    db.session.add(signature)                 # add a row to database
    db.session.commit()                     # save changes

    return redirect(url_for('index'))
    return render_template('index.html', name=name, comment=comment)

@app.route('/searchresults', methods=['GET', 'POST'])
def searchresults():
    name = request.form['name']
    result = Comments.query.filter_by(name=name)
    counts = result.count()
    return render_template('index.html', result=result, counts=counts)

if __name__ == "__main__":
   db.create_all()
   app.run(host='0.0.0.0', port=80)