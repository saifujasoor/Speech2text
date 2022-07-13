import speech_recognition as sr
from flask import logging, Flask, render_template, request, flash
from subprocess import run, PIPE
import os
from flask import request, abort, render_template
from flask import send_file, send_from_directory
import video_structuring as vy
import librosa
import deep_speech as deep_speech
import cmu_sphinx as cmu_sphinx
import audioop
from flask_cors import CORS
import wave
from werkzeug.utils import secure_filename

#CORS(app)

#app.config["DEBUG"] = True

app = flask.Flask(__name__)
app.secret_key = "VatsalParsaniya"

@app.route('/')
def index():
    flash(" Welcome to Solution")
    return render_template('index.html')

@app.route('/audio_to_text/')
def audio_to_text():
    flash(" Press Start to start recording audio and press Stop to end recording audio")
    return render_template('audio_to_text.html')


@app.route('/audio', methods=['POST'])
def audio():
    r = sr.Recognizer()
    with open('upload/audio.wav', 'wb') as f:
        f.write(request.data)
  
    with sr.AudioFile('upload/audio.wav') as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data, language='en-IN', show_all=True)
        print(text)
        return_text = " Did you say : <br> "
        try:
            for num, texts in enumerate(text['alternative']):
                return_text += str(num+1) +") " + texts['transcript']  + " <br> "
        except:
            return_text = " Sorry!!!! Voice not Detected "
        
    return str(return_text)


# Speech To Text

@app.route('/Speech_to_text/')
def Speech_to_text():
    flash(" Press Start to start recording audio and press Stop to end recording audio")
    return render_template('index1.html')


def combine(method, name):
    path = "Files/"
    video =  name
    audio, transcript = vy.home(path, video)
    res = ""
    if method=='deepspeech':
        res = deep_speech.func(audio, transcript)
    elif method=='cmu':
        res = cmu_sphinx.func(audio, transcript)
    return(res)

@app.route('/generate_transcript', methods=['POST'])
def home():
    #print(request.get_data())
    print('form',request.form)
    file=request.files['file']
    model=request.form['method']
    print(model)
    if request.method == "POST":
        with open('audio.wav', 'wb') as f:
            #print(file.read())
            f.write(file.read())
        print('file uploaded successfully')
        f.close()
    #proc = run(['ffprobe', '-of', 'default=noprint_wrappers=1', 'audio.wav'], text=True, stderr=PIPE)
    #with open('audio.wav', 'wb') as f:
     #   f.write(proc)


    if 'file' not in request.files:
        print('file',request.files)
        abort(400)

    elif 'method' not in request.form:
        print('method',request.form)
        abort(400)

    print(request.files)
    file_request = request.files['file']
    content_type_file = file_request.content_type

    print(file_request)
    print(request.form['method'])

    if "video" in content_type_file:
        print("video")
    elif "audio" in content_type_file:
        print("audio")
    else:
        abort(403)

    """

    filename = secure_filename(file_request.filename)
    file_request.save(os.path.join('Files/Video', filename))
    print("saved file successfully")
    """
    video_name = 'audio.wav'
    audioFile = wave.open(video_name, 'r')
    n_frames = audioFile.getnframes()
    audioData = audioFile.readframes(n_frames)
    originalRate = audioFile.getframerate()
    af = wave.open('audioData.wav', 'w')
    af.setnchannels(1)
    af.setparams((1, 2, 16000, 0, 'NONE', 'Uncompressed'))
    converted = audioop.ratecv(audioData, 2, 1, originalRate, 16000, None)
    af.writeframes(converted[0])
    af.close()
    audioFile.close()
    video_name='audioData.wav'
    #audioFile.close()

    #w=wave.open(video_name,'r')

    print('channels',audioFile.getnchannels())

    #print(video_name)

    return(combine(model, video_name))
    
@app.route('/download_transcript', methods=['GET'])
def download():
    return send_file(os.path.join('Files/Transcript/output.txt'), attachment_filename="output.txt", as_attachment=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5002')
