
##########################################################################################################################

# Imports
from flask import Flask, request, Response
from json import dumps

# Modules
from .canlii import find
from .ai import summarize

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
        
        # Run OpenAI Summarizer
        summarized = summarize(cases)
        
        # Return Data
        return Response(
            dumps(summarized),
            mimetype = 'application/json'
        )
    except Exception as error:
        return Response('', status=501)

##########################################################################################################################
