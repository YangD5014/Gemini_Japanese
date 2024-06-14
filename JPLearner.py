import pathlib
import textwrap

import google.generativeai as genai
import html2text,re
import azure.cognitiveservices.speech as speechsdk
import pdfkit
import time
# from IPython.display import display
# from IPython.display import Markdown
from pykakasi import kakasi
# from md2pdf.core import md2pdf
import markdown
import logging
from bs4 import BeautifulSoup
genai.configure(api_key='AIzaSyAo2VAV4eGFv5wqByYUw6yP-Sjh8Va9z5c')

class JPLearner:
    def __init__(self, word_list: str):
        self.word_list = word_list
        self.logger_init(logger_name=str(time.time()))
        self.prepare()
        self.separate_stroy()
        self.id=time.time()
        #self.read_story()
        #self.generate_pdf()
        
        
    def logger_init(self,logger_name:str=__name__):
        # 定义记录器对象
        self.logger = logging.getLogger(logger_name)
        # 设置记录器级别
        self.logger.setLevel(logging.DEBUG)
        # 设置过滤器 只有被选中的可以记录
        myfilter = logging.Filter(logger_name)
        # 定义处理器-文件处理器
        filehandler = logging.FileHandler(filename=str(logger_name+'.log'), mode='w')
        filehandler.addFilter(myfilter)
        # formatter = logging.Formatter('%(asctime)s-%(levelname)s-\n%(message)s')
        # filehandler.setFormatter(formatter)
        # 定义处理器-控制台处理器
        concolehander = logging.StreamHandler()
        concolehander.setLevel(logging.INFO)
        # 记录器绑定handerler
        self.logger.handlers.clear()
        self.logger.addHandler(filehandler)
        self.logger.addHandler(concolehander)
        self.logger.info('logger init done!')
    
    def prepare(self):
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.chat = self.model.start_chat(history=[])
        self.prompt = "我是一个在学习日语的中国大学生,我希望你能够帮我学习新学习到的词汇,我将会给你一些新学到的词汇,\
            请你基于我给出的词汇,写一篇日文短文,使得这些词汇都能够被用到。我将会使用符号分割他们。你的回答按照如下结构:<h2>短文故事</h2>;<h2>短文中文翻译</h2>;<h2>词汇解释</h2>"
        self.response = self.chat.send_message(self.prompt)
        self.response = self.chat.send_message(self.word_list)
        self.html = markdown.markdown(self.response.text)
        self.response.stroy = self.html
        self.logger.info(f'Gemini response already done!')
        
        
    def separate_stroy(self):
        self.story_paragraph =[]
        self.aferhtml_story_paragraph = []
        self.afermd_story_paragraph = []
        self.soup = BeautifulSoup(self.html, 'html.parser')
        h2_tags = self.soup.find_all('h2')
        # 找到<h2>标签后的所有兄弟节点，直到下一个<h2>标签
        for sibling in h2_tags[0].find_next_siblings():
            if sibling.name == 'h2':
                break
            if sibling.name == 'p':
                # print(sibling.text)
                self.story_paragraph.append(sibling.text)
                after_html,after_md = JPLearner.假名注音(sentence=sibling.text)
                after_html = '<p>'+after_html+'</p>'
                print(after_html)
                #sibling.string.replace_with(after_html)
                self.aferhtml_story_paragraph.append(after_html)
                self.afermd_story_paragraph.append(after_md)
                #print(after_html,after_md)
                        
        self.story_paragraph  = ''.join(self.story_paragraph)
        self.aferhtml_story_paragraph = ''.join(self.aferhtml_story_paragraph)
        self.aferhtml_story_paragraph 
        
        self.afermd_story_paragraph = ''.join(self.afermd_story_paragraph)
        self.aferhtml = self.soup
        # self.logger.info(f'After html:{self.aferhtml}')
        # self.logger.info(f'短文正文:{self.story_paragraph}')
                # 定义替换函数
        def replace_content(match):
            h2_tag = match.group(1)
            content = match.group(2)
            # 删除第一个 <h2> 标签后的所有 <p> 标签内容
            p_pattern = re.compile(r'<p>.*?</p>', re.DOTALL)
            new_content = p_pattern.sub('', content)
            # 插入新的内容
            new_content = self.aferhtml_story_paragraph + '<h2>'
            return h2_tag + new_content

        
        pattern = re.compile(r'(<h2>.*?</h2>)(.*?)<h2>', re.DOTALL)
        # 进行匹配
        self.modified_html_content = pattern.sub(replace_content,self.html)
        
                        
        
    @staticmethod
    def 假名注音(sentence:str):   
        #假名注音
        kakasi_instance = kakasi()
        result = kakasi_instance.convert(sentence)
        after_text_html = ''
        after_text_md = ''
        for each_converted in result:
            if each_converted['orig'] == each_converted['hira']:
                after_text_html += each_converted['orig']
                after_text_md += each_converted['orig']
            else:
                after_text_html += r'<ruby>'+each_converted["orig"]+'<rt>'+each_converted["hira"]+'</rt></ruby>'
                
                after_text_md += f'{each_converted["orig"]}({each_converted["hira"]})'
                
        #print(after_text_html)
        return after_text_html,after_text_md
        
    def read_story(self):
        speech_config = speechsdk.SpeechConfig(subscription='576c74fce86a41bdae3473085ce32be7', region='japaneast')
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(self.id)+'.mp3')
        speech_config.speech_synthesis_voice_name='ja-JP-KeitaNeural'
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)   
        speech_synthesis_result = speech_synthesizer.speak_text_async(self.story_paragraph).get()
        
    def generate_pdf(self):
        #版本1：mardown转pdf
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        options = {
        'no-stop-slow-scripts': None,
        'image-quality': '100',
        'enable-local-file-access': None,
        'margin-top': '20',
        'page-size': 'A4',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
        # 'orientation': 'Landscape',  # 设置为横版
        'encoding': "UTF-8"}
        # html_text = markdown.markdown(self.story_paragraph)
        pdfkit.from_string(self.modified_html_content, str(id)+'.pdf',configuration=config,options=options)
        with open('output_new.html', 'w', encoding='utf-8') as file:
            file.write(self.modified_html_content)
        self.logger.info('PDF生成成功') 
        
        # 使用 html2text 将 HTML 内容转换为 Markdown
        # h = html2text.HTML2Text()
        # h.ignore_links = True  # 可选：忽略链接

        # markdown_content = h.handle(html_content)