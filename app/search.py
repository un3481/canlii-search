
##########################################################################################################################

# Imports
from json import loads
from requests import get
from typing import TypedDict

##########################################################################################################################

class Case(TypedDict):
    province: str
    id: str
    title: str
    url: str

##########################################################################################################################

base = 'https://www.canlii.org'

##########################################################################################################################

def find(full_name: str, provinces: list[str], court: bool, tribunal: bool):
    try:
        # Get search URL
        if len(provinces) == 0: provinces.append('ca')
        _provinces: str = ','.join(provinces)
        search_url = f'{base}/en/search/ajaxSearch.do?jId={_provinces},unspecified&text="{full_name}"&origJId=ca'
        
        # Set Variable
        cases: list[Case] = []

        # Loop over pages
        fetched_pages: bool = False
        pages: list[str] = ['1']
        
        while True:
            # Pop page from list
            page: str = None
            try: page = pages.pop(0)
            except Exception: break
            
            # Request Page
            res = get(f'{search_url}&page={page}')

            # Check status
            if res.status_code != 200:
                raise Exception('Could not fetch json')

            # Check JSON
            res_json = res.json()
            if not isinstance(res_json, dict):
                raise Exception('Invalid response')
            
            # Handle Pagination
            if not fetched_pages:
                fetched_pages = True
                
                # Check pages list
                res_pages: list[dict] = loads(res_json['pages'])
                
                # Extract pages
                for res_page in res_pages:
                    if res_page['id'] != '1':
                        pages.append(res_page['id'])

            # Check results list
            results: list = res_json['results']

            # Extract cases
            for result in results:
                # Check case
                if not isinstance(result, dict):
                    continue
                if result['path'] == None:
                    continue
                # Append case
                cases.append(Case(
                    province = result['jurisdictionId'],
                    id = result['concatId'],
                    title = result['title'],
                    url = f'{base}{result["path"]}'
                ))
        
        # Return data
        return True, cases
    except Exception as error:
        return False, error

##########################################################################################################################
