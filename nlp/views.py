from flask import render_template
from flask_restplus import Resource, Namespace
from nlp import app, api

# This function doesn't work for some reason
@app.route('/')
def index():
    return render_template('index.html')

# This function does
@app.route('/index')
def show_index():
    return render_template('index.html')


@app.route('/universities')
def show_uni_list():
    return render_template('university_list.html')

ns = Namespace('api', description='API Operations')

@ns.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {"Hello": "World"}

    def post(self):
        return {"Hello": "World"}


#@api.route('/api/id/<int:id>')
@ns.route('/id/<int:id>')
@ns.param('id', 'ID Thing')
class ID(Resource):
    def get(self, id):
        return {"ID" : id}


api.add_namespace(ns)

