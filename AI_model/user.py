import gradio as gr
import tiktoken
import json
# from azure_util.gpts import *
from gpts import *
from duckduckgo_search import DDGS
# from funcs import Audio_agent
import requests


def cal_token_num(history):
    content = ''
    for c in history:
        content += c['content']
    res = (tiktoken.get_encoding('cl100k_base').encode(content))
    # print(res)
    return res


def duckduckgo(query, mode, region, save_search, max_results=10):
    if mode == 'chat':
        return query
    if mode == 'search':
        results = DDGS().text(query, region, save_search, max_results=max_results)  # 获取前5条结果
        search_results_text = "\n\n".join(
            [f"标题: {result['title']}\n链接: {result['href']}\n摘要: {result['body']}" for result in results]
        )
    if mode == 'news':
        results = DDGS().news(query, region, save_search, max_results=max_results)  # 获取前5条结果
        search_results_text = "\n\n".join(
            [f"标题: {result['title']}\n链接: {result['url']}\n摘要: {result['body']}" for result in results]
        )
        print(results)

    # 将搜索结果整理为文本

    return f"请根据以下搜索结果回答：{query}\n\n{search_results_text}"


def predict_block(system, system1,user_radio, history, mode, search_num, region, save_search, memory_num, version, temperature):
    import random
    if random.random() > 1-user_radio:
        cont = f"你要扮演一个角色，人格描述是：{system}"
    else:
        cont = f"你要扮演一个角色，人格描述是：{system}。下面将要和你对话的朋友，人格描述为：{system1}。"

    history_openai_format = [{"role": "system", "content": cont}]
    idx = 0

    history[-1][0] = duckduckgo(history[-1][0], mode, region.split()[0], save_search, search_num)

    for human, assistant in history:  # re-build all history, live system alone
        history_openai_format.append({"role": "user", "content": human})
        if assistant is not None:
            history_openai_format.append({"role": "assistant", "content": assistant})
        idx += 1
        if idx > memory_num:
            history_openai_format.pop(0)
            history_openai_format.pop(0)
    response = openai_core(history_openai_format, version, temperature, stream=True)

    partial_message = ""
    for chunk in response:
        try:
            tmp = chunk.choices[0].delta.content
        except:
            tmp = ''
        if tmp:
            partial_message += tmp

        history[-1][1] = partial_message
        yield history, cal_token_num(history_openai_format)


def predict_block_direct(system, history, mode, search_num, region, save_search, memory_num, version, temperature):
    history_openai_format = [{"role": "system", "content": system}]
    idx = 0

    history[-1][0] = duckduckgo(history[-1][0], mode, region.split()[0], save_search, search_num)

    for human, assistant in history:  # re-build all history, live system alone
        history_openai_format.append({"role": "user", "content": human})
        if assistant is not None:
            history_openai_format.append({"role": "assistant", "content": assistant})
        idx += 1
        if idx > memory_num:
            history_openai_format.pop(0)
            history_openai_format.pop(0)
    response = openai_core(history_openai_format, version, temperature)
    text = response.choices[0].message.content
    output_file = text_to_audio(text)
    history[-1][1] = text
    return history, output_file


def user(user_message, history):
    print('$$$$$$$$$$$$>>>>', history)
    return "", history + [[user_message, None]]


def auth(user, pwd):
    with open("../auth.json", 'r') as s:
        d = json.load(s)
        if user in d['gpt'].keys():
            if d['gpt'][user] == pwd:
                return True
    return False


def load_model_sorted(path):
    with open(path, 'r') as f:
        res = f.readlines()
    return [i[:-1] for i in res]


def load_region(path):
    with open(path, 'r') as f:
        res = f.readlines()
    return [i[:-1] for i in res]


def load_personas(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def change_persona(key, path):
    data = load_personas(path)
    return data[key]


def save_persona(key, value, path):
    data = load_personas(path)
    data[key] = value
    # 写入JSON文件
    with open(path, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)
    return


def make_persona(persona, user_persona, version, temperature):
    sys = f'''你扮演一个角色，人格描述是：{persona}，从你的眼光判断，并合理发散幻想一下，下面你这位朋友的人格描述。
        请用一整段文字进行回复，不要出现1.2.3的条目。
        请检查基本信息，不要与客观基本信息有任何出入。
        请尽量详细的设想这个人的其他方面，甚至包括他可能喜欢什么讨厌什么，回复尽量详细。'''
    user = f"这个人的基本信息为：{user_persona}"
    res = call_openai(sys, user, version, temperature)
    return res


def audio_to_text(filepath, history):
    # user_message = audio_agent.decode_file(filepath)  ## ncnn onnx
    url = "https://api.siliconflow.cn/v1/audio/transcriptions"
    headers = {
        "Authorization": "Bearer sk-bmubgnwlyhbppwkverbshqyotfklcvgqsvysqlqpydhngnzs"
    }
    files = {
        "file": open(filepath, "rb")  # 以二进制模式打开文件
    }
    data = {
        "model": "FunAudioLLM/SenseVoiceSmall"
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    user_message = json.loads(response.text)['text']
    return None, history + [[user_message, None]]


def text_to_audio(text):
    # output_file = audio_agent.create_maker(text)
    output_file = 'output.wav'
    url = "https://api.siliconflow.cn/v1/audio/speech"
    payload = {
        "model": "fishaudio/fish-speech-1.5",
        "input": text,
        "voice": "fishaudio/fish-speech-1.5:alex",
        "response_format": "wav",
    }
    headers = {
        "Authorization": "Bearer sk-bmubgnwlyhbppwkverbshqyotfklcvgqsvysqlqpydhngnzs",
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    with open(output_file, "wb") as wav_file:
        wav_file.write(response.content)

    return output_file


if __name__ == "__main__":
    custom_css = """
    #chatbot-container { 
        height: 60vh !important; /* 占据整个屏幕高度 */
    }
    #chatbot-txt { 
        height: 20vh !important; /* 占据整个屏幕高度 */
    }
    #chatbot-btn { 
        height: 20vh !important; /* 占据整个屏幕高度 */
    }
    """
    # dropdown_options = ["openai/gpt-4o-2024-11-20", "openai/gpt-4o-mini"]
    dropdown_options = load_model_sorted('./models.txt')
    region_options = load_region('./region.txt')
    personas = load_personas('./persona.json')
    personas_keys = list(personas.keys())
    user_personas = load_personas('./user.json')
    user_personas_keys = list(user_personas.keys())
    # audio_agent = Audio_agent()

    # gr.ChatInterface(predict).launch()
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(show_copy_button=True, elem_id="chatbot-container")
        with gr.Row(visible=False):
            rec = gr.Audio(sources=['microphone'], type="filepath")
            rec_btn = gr.Button('submit')
            rec_resp = gr.Audio(type="filepath")

        msg = gr.Textbox(elem_id="chatbot-txt")
        with gr.Row(elem_id="chatbot-btn"):
            with gr.Column():
                token_num = gr.Slider(minimum=0, maximum=4000, value=0, label='token num', visible=False,
                                      interactive=False)
                memory_num = gr.Number(value=10, label='memory num', interactive=True)
                temperature = gr.Number(value=0.7, label='temperature', interactive=True)
            with gr.Column():
                mode = gr.Dropdown(value='chat', choices=['chat', 'search', 'news'])
                search_num = gr.Number(value=5, label='search num', interactive=True)
            with gr.Column():
                region = gr.Dropdown(value='cn-zh for China', choices=region_options)
                save_search = gr.Dropdown(value='moderate', choices=['moderate', 'off'])
            with gr.Column():
                model = gr.Dropdown(value=dropdown_options[0], choices=dropdown_options)
                clear = gr.Button('clear')
        with gr.Row():
            with gr.Column():
                persona_opt = gr.Dropdown(value=personas_keys[0], choices=personas_keys)
                user_ratio = gr.Number(value=0.1, label='ratio about user', interactive=True)
                persona_txt = gr.Textbox(label='persona', lines=5, value=personas[personas_keys[0]])
                persona_save = gr.Button('save change')
            with gr.Column():
                user_persona_opt = gr.Dropdown(value=user_personas_keys[0], choices=user_personas_keys)
                user_persona_txt = gr.Textbox(label='user persona', lines=5, value=user_personas[user_personas_keys[0]])
                user_persona_save = gr.Button('save change')
                # user_persona_make = gr.Button('make real persona')
                # user_persona_txt_real = gr.Textbox(label='real persona', lines=5)

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            predict_block,
            [persona_txt, user_persona_txt, user_ratio, chatbot, mode, search_num, region, save_search, memory_num, model,
             temperature],
            [chatbot, token_num]
        )

        persona_opt.change(lambda x: change_persona(x, 'persona.json'), inputs=[persona_opt], outputs=[persona_txt])
        persona_save.click(lambda x, y: save_persona(x, y, 'persona.json'), inputs=[persona_opt, persona_txt])
        user_persona_opt.change(lambda x: change_persona(x, 'user.json'), inputs=[user_persona_opt],
                                outputs=[user_persona_txt])
        user_persona_save.click(lambda x, y: save_persona(x, y, 'user.json'),
                                inputs=[user_persona_opt, user_persona_txt])
        # user_persona_make.click(make_persona, inputs=[persona_txt, user_persona_txt, model, temperature],
        #                         outputs=[user_persona_txt_real])

        clear.click(lambda: None, None, chatbot, queue=False)

        rec_btn.click(
            audio_to_text, inputs=[rec, chatbot], outputs=[rec, chatbot]
        ).then(
            predict_block_direct,
            [persona_txt, chatbot, mode, search_num, region, save_search, memory_num, model, temperature],
            [chatbot, rec_resp]
        )

    demo.queue()
    demo.launch(
        # server_name='0.0.0.0',
        server_port=19001, show_api=False,
        # auth=auth,
        root_path="/gpt")
