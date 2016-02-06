from flask import Flask, render_template, request, redirect, url_for, json
from werkzeug import secure_filename
from pyelasticsearch import ElasticSearch
from subprocess import call
import os

app = Flask(__name__)
es = ElasticSearch('http://localhost:9200/')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        try:
            query = request.form['query']
            result = es.search(query=query, index='documents')
        except:
            return render_template('query.html', error=query)
        return render_template('query.html', result=result)
    return render_template('query.html')

@app.route("/query", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        print file
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'documents.json'))
            return redirect(url_for('home', filename=filename))
    if request.args.get('filename'):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, UPLOAD_FOLDER, request.args.get('filename'))
        call(["elasticdump", "--bulk=true", "--input=" + json_url, "--output=http://localhost:9200/"])
        return render_template('home.html', status="upload success")
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
