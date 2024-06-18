
from flask import request, jsonify
from flask import Flask,render_template
from JPLearner import JPLearner
import azure.cognitiveservices.speech as speechsdk
import pdfkit

app = Flask(__name__)

audio_dir = 'static/music/'
pdf_dir = 'static/pdf/'

@app.route('/')
def index():
    audio_filename = '1718390958.4828665.mp3'
    return render_template('index.html',audio_filename=audio_filename)

@app.route('/Gemini', methods=['POST'])
def generateAnswer():
    data = request.json
    sentence = data['words']
    result = JPLearner(word_list=sentence)
    
    def read_story(self):
        speech_config = speechsdk.SpeechConfig(subscription='576c74fce86a41bdae3473085ce32be7', region='japaneast')
        audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_dir+str(self.id)+'.mp3')
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
        pdfkit.from_string(self.modified_html_content,  'static/pdf/'+str(self.id)+'.pdf',configuration=config,options=options)
        with open('output_new.html', 'w', encoding='utf-8') as file:
            file.write(self.modified_html_content)
        self.logger.info('PDF生成成功') 
        
    audio_filename = 'static/music/'+str(result.id)+'.mp3'
    pdf_filename = 'static/pdf/'+str(result.id)+'.pdf'
    read_story(result)
    generate_pdf(result)
    return jsonify({'receive':sentence,'id':result.id,'html_code':result.modified_html_content,'content':'kls','audio_filename':audio_filename,'pdf_filename':pdf_filename})


if __name__ == '__main__':
    app.run(port=8000, debug=True)