
##########################################################################################################################

# Imports
from flask import Flask, request, Response
from json import dumps

from .canlii import find
from .ai import summarize

##########################################################################################################################

# Declare WSGI app
app = Flask('canlii_search_app')

# Search route
@app.route('/search/', methods=['GET'])
async def search():
    try:
        args = request.args
        full_name = args.get('fullname', default=None, type=str)
        provinces = args.get('provinces', default=None, type=list)
        tribunal = args.get('tribunal', default="yes", type=str)
        court = args.get('court', default="yes", type=str)
        
        if full_name == None:
            return Response('', status=400)
        
        if provinces == None: provinces = []
        if len(provinces) > 0:
            for province in provinces:
                if not isinstance(province, str):
                    return Response('', status=400)
        
        # Run Search
        search_ok, cases = find(full_name, provinces, court=="yes", tribunal=="yes")
        if not search_ok: raise cases
        
        # Run OpenAI Summarizer
        summarized = await summarize(cases)
        
        # Return Data
        return Response(
            dumps(summarized),
            mimetype = 'application/json'
        )
    except Exception as error:
        return Response('', status=501)

##########################################################################################################################
