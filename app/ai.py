
##########################################################################################################################

# Imports
from os import getenv
from time import sleep
from random import randint
from threading import Thread
from multiprocessing import Queue

import openai

# Modules
from .canlii import Case, download_text

##########################################################################################################################

openai.api_key = getenv('OPENAI_API_KEY')

##########################################################################################################################

def summarize_text(text: str, retry: int = 0):
    try:
        # Turn into a question 
        question = f'Summarize following text (mention the names of the parts involved and give an answer between 300 and 500 characters): \n\n{text}'
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
                    max_tokens=500,
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

def summarize_iter(case: Case, text: str, queue: Queue):
    # Summarize
    summary_ok, summary = summarize_text(text, retry=10)
    if summary_ok: case['summary'] = summary
    else: print(f'openai error: {summary}')
    
    # Return data
    queue.put(case)

##########################################################################################################################

def summarize(cases: list[Case]):
    # Init Queue
    summarized_queue = Queue()
    
    # Spawn threads
    threads: list[Thread] = []
    first: bool = True
    for case in cases:
        # Prevent Download Rate-Limit
        if not first:
            first = False
            sleep(randint(20, 30))
        
        # Download PDF text
        pdf_ok, text = download_text(case['url'])
        if not pdf_ok:
            summarized_queue.put(case)
            continue
        
        # Spawn Thread
        thread = Thread(target=summarize_iter, args=(case, text, summarized_queue))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Join all threads
    for thread in threads:
        thread.join()
    
    # Extract data from Queue
    summarized: list[Case] = []
    while True:
        case: Case = None
        try: case = summarized_queue.get(block=False)
        except Exception: break
        summarized.append(case)
    
    # Return summarized cases
    return summarized

##########################################################################################################################
