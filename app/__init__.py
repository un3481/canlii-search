
##########################################################################################################################

# Imports
from flask import Flask, request, Response
from json import dumps

# Modules
from .search import find
from .summary import extract_text, summarize

##########################################################################################################################

# Declare WSGI app
app = Flask('canlii_search_app')

# Search route
@app.route('/search/', methods=['GET'])
def search():
    try:
        args = request.args
        full_name = args.get('fullname', default=None, type=str)
        provinces = args.get('provinces', default=None, type=str)
        tribunal = args.get('tribunal', default='yes', type=str)
        court = args.get('court', default='yes', type=str)
        
        if full_name == None:
            return Response('', status=400)
        
        if provinces == None: provinces = 'ca'
        provinces = provinces.split(',')
        
        # Run Search
        search_ok, cases = find(full_name, provinces, court=='yes', tribunal=='yes')
        if not search_ok: raise cases
        
        # Return Data
        return Response(
            dumps(cases),
            mimetype = 'application/json'
        )
    except Exception as error:
        return Response('', status=501)

##########################################################################################################################

# Summary route
@app.route('/summary/', methods=['POST'])
def summary():
    try:
        files = request.files
        file = files.get('file', default=None)
        
        if file == None:
            return Response('', status=400)
        
        # Extract text from file
        _bytes = file.stream.read()
        text_ok, text = extract_text(_bytes)
        if not text_ok: raise text
        
        # Run OpenAI Summarize
        summarize_ok, answer = summarize(text, retry=10)
        if not summarize_ok: raise answer
        
        # Return Data
        return Response(
            dumps({'answer': answer}),
            mimetype = 'application/json'
        )
    except Exception as error:
        return Response('', status=501)

##########################################################################################################################
