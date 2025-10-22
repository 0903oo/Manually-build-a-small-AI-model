import func_timeout
from func_timeout import func_set_timeout
from openai import OpenAI
import requests
import json

@func_set_timeout(100)
def openai_core(msg, version, temperature=0, stream=False):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key='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'  )
    return client.chat.completions.create(
        # model='openai/gpt-4o-2024-11-20',
        # model='openai/gpt-4o-mini',
        model=version,
        messages=msg,
        temperature=temperature,
        max_tokens=3000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=stream
    )



def call_openai(sys, user, version='gpt-4o-mini', temperature=0, max_test_num=3):
    msg = [{"role": "system", "content": sys}, {"role": "user", "content": user}]
    idx = 0
    while idx < max_test_num:
        idx += 1
        try:
            response = openai_core(msg, version, temperature)
            return response.choices[0].message.content
        except func_timeout.exceptions.FunctionTimedOut as e:
            print(e)
            print('single gpt request time out!')
        finally:
            print('error pls wait...')