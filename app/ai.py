
##########################################################################################################################

# Imports
import os
import openai

from .canlii import Case, download_text

openai.api_key = os.getenv("OPENAI_API_KEY")

##########################################################################################################################

def summarize_text(text: str):
    try:
        # Turn into a question 
        question = f"Summarize following text (mention the names of the parts involved and give an answer between 300 and 500 characters):\n\n{text}"
        
        # Ask question to openai model
        answer: str = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            temperature=0.5,
            max_tokens=1000,
        )["choices"][0]["text"]
        
        # Check answer
        if not isinstance(answer, str):
            raise "invalid answer"
        
        # Return data
        return True, answer
    except Exception as error:
        return False, error

##########################################################################################################################

async def summarize_iter(case: Case):
    # Download PDF text
    pdf_ok, text = download_text(case["url"])
    if not pdf_ok: return case
    
    # Summarize
    summary_ok, summary = summarize_text(text)
    if summary_ok: case["summary"] = summary
    
    # Return data
    return case

##########################################################################################################################

async def summarize(cases: list[Case]):
    # Spawn threads
    threads = list(map(summarize_iter, cases))
    
    # Await all threads
    summarized_cases: list[Case] = []
    for thread in threads:
        summarized_cases.append(await thread)
        
    # Return summarized cases
    return summarized_cases

##########################################################################################################################
