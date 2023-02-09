
##########################################################################################################################

# Imports
from json import loads
from requests import get
from typing import TypedDict
from PyPDF2 import PdfFileReader

##########################################################################################################################

class Case(TypedDict):
    province: str
    title: str
    url: str
    summary: str

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
                    title = result['title'],
                    url = f'{base}{result["path"]}',
                    summary = ''
                ))
        
        # Return data
        return True, cases
    except Exception as error:
        return False, error
    

##########################################################################################################################

def download_text(url: str):
    try:
        pdf_url = url.replace('.html', '.pdf')
        res = get(pdf_url)

        # Check status
        if res.status_code != 200:
            raise Exception(f'Could not download file')

        # Check mimetype
        mimetype = res.headers.get('content-type', default='').lower()
        if mimetype != 'application/pdf':
            raise Exception('Invalid MIME type')

        # Extract text from PDF
        _pdf = PdfFileReader(res.content)
        _page = _pdf.getPage(_pdf.numPages + 1)
        text = _page.extractText()
        
        # Return data
        return True, text
    except Exception as error:
        return False, error

##########################################################################################################################
