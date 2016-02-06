from flask import Flask, render_template, request, redirect, url_for, json
from werkzeug import secure_filename
from pyelasticsearch import ElasticSearch
from subprocess import call
import os, string

app = Flask(__name__)
es = ElasticSearch('http://localhost:9200/')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=['GET', 'POST'])
def query():
    query_list = ['id', 'content', 'station_id', 'url', 'name', 'local_name',       \
            'status', 'type', 'processing', 'service', 'callsign', 'partycity',     \
            'invoice_in_name', 'invoice_in_content', 'uploaded_timestamp',          \
            'downloaded_timestamp', 'meta_creation', 'meta_modification', 's3_name']
    if request.method == 'POST':
        try:
            q = {"query":{"match_all":{}}}
            req = string.replace(request.form['query'], "'", '"')
            print request.form
            a = request.form['select']
            print request.form.getlist('select'), 'list'
            
            for item in request.form.getlist('select'):
                print request.form[item]
            
            query = json.loads(json.loads(json.dumps(req)))
            result = json.dumps(es.search(query=query, index='documents'))
        except:
            return render_template('query.html', error=q, lists=query_list)
        return render_template('query.html', result=result, lists=query_list)
    return render_template('query.html', lists=query_list)

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
