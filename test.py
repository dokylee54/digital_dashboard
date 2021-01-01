#!/usr/bin/env python
from flask import Flask, url_for, render_template, send_from_directory, request
import jinja2.exceptions
import pickle

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['POST', 'GET'])
def form():
    
    if request.method == 'POST':
        result = request.form.to_dict()
        print('POST of /form', result['teamname'])
        
        with open('data.pickle', 'wb') as f:
            pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)
        
        return render_template('form.html', result=result)
    
    return render_template('form.html')

@app.route('/form_write', methods=['GET'])
def form_write():
    return render_template('form_write.html')

@app.route('/<pagename>')
def admin(pagename):
    return render_template(pagename+'.html')

@app.route('/<path:resource>')
def serveStaticResource(resource):
	return send_from_directory('static/', resource)

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(404)
def not_found(e):
    return '<strong>Page Not Found!</strong>', 404

if __name__ == '__main__':
    app.run()
