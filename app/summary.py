
##########################################################################################################################

# Imports
from os import getenv
from io import BytesIO
from time import sleep
from PyPDF2 import PdfReader

import openai

##########################################################################################################################

openai.api_key = getenv('OPENAI_API_KEY')

##########################################################################################################################

def extract_text(content: bytes):
    try:
        # Create PDF
        _content = BytesIO(content)
        _pdf = PdfReader(_content)
        
        # Extract text from PDF
        text = ''
        for page in _pdf.pages:
            text += page.extract_text()
            text += '\n\n'
            if len(text) > 10000: break
        
        # Return data
        return True, text
    except Exception as error:
        return False, error

##########################################################################################################################

def summarize(text: str, retry: int = 0):
    try:
        # Turn into a question 
        question = f'Summarize following text explaining the decision, mentioning the names of the parts involved, and do not exceed 500 characters in your answer: \n\n{text}'
        answer: str = ''
        
        # Retry the specified number of times
        trials = 0
        while True:
            try:
                # Ask question to openai model
                answer = openai.Completion.create(
                    model='text-davinci-003',
                    prompt=question,
                    temperature=0.5,
                    max_tokens=300,
                )['choices'][0]['text']

                # Check answer
                if not isinstance(answer, str):
                    raise Exception('invalid answer')

                break
            except Exception as error:
                trials += 1
                if trials > retry: raise error
                else: sleep(1)
        
        # Return data
        return True, answer
    except Exception as error:
        return False, error

##########################################################################################################################
