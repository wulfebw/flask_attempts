import os
import sys
import time

try:
    user_paths = os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
except KeyError:
    print("error")
    user_paths = []

if not user_paths:
    os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib'
    print("setting user paths")
    print(os.environ['LD_LIBRARY_PATH'])
if not user_paths:
    sys.path.insert(0, '/usr/local/lib')
    print("setting user paths")
    print(sys.path)

print(user_paths)

try:
    import pocketsphinx as ps
except:
    print("pocketsphinx failed")

try:
    import nltk
except:
    print("nltk failed")


# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from werkzeug.contrib.fixers import ProxyFix
from decode_speech import decode_speech_driver, decode_speech

import logging
from logging.handlers import RotatingFileHandler

from utils import stereo_to_mono, get_duration, new_filename

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'wav', 'webm'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('recordrtc_index.html')

def log_request_info(request):
    app.logger.warning("\n\n\n\n\n\nNEW LOG\ntime:".format(time.time()))
    app.logger.warning("request.path: {0}".format(request.path))
    app.logger.warning("request.script_root: {0}".format(request.script_root))
    app.logger.warning("request.host: {0}".format(request.host))
    app.logger.warning("request.url: {0}".format(request.url))
    app.logger.warning("request.method: {0}".format(request.method))
    app.logger.warning("request.args.keys(): {0}".format(request.args.keys()))
    app.logger.warning("request.form.keys(): {0}".format(request.form.keys()))
    app.logger.warning("request.files: {0}".format(request.files))
    app.logger.warning("request.headers: {0}".format(request.headers))

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    

    # app.logger.warning(request)
    log_request_info(request)
    # video is a werkzeug.datastructures.FileStorage object
    video = request.files['video-blob']
    app.logger.warning(video)
    # app.logger.warning(video['contents'])
    app.logger.warning(type(video))
    # data = video.read()
    # app.logger.warning(data)
    app.logger.warning("filename: {0}".format(video.filename))
    audio = request.files['audio-blob']
    app.logger.warning(audio)
    # data = audio.read()
    # app.logger.warning(len(data))

    try:
        # Get the name of the uploaded file
        # file = request.files['file']
        video = request.files['video-blob']
        audio = request.files['audio-blob']
    except Exception as e:
        app.logger.warning("error: {0}".format(e))
        raise Exception(e)
    
    # let's time it
    start = time.time()

    video_filename = ''
    audio_filename = ''

    if video: # and allowed_file(video.filename):
        # data = video.read()
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(video.filename) + '_video' + '.webm'
        video_filename = filename
	# Move the file form the temporal folder to
        # the upload folder we setup
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        # return redirect(url_for('uploaded_file',
        #                         filename=filename))
    if audio:
        audio_filename = secure_filename(audio.filename) + '_audio'+  '.wav' #.mp3?
	print("AUDIO_1!!!: {0}".format(audio_filename))
#        audio_filename = new_filename(filename, "_mono")
	audio.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))
        app.logger.warning("filename: {0}".format(audio_filename))
        stereo_to_mono(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))
	audio_filename = new_filename(audio_filename, "_mono")
	audio_filename = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        outfilename = '/home/ec2-user/flask_attempts/data/test.txt'
        stats = dict()
	# decode the speech in the file
        #ling_stats = decode_speech_driver(filename, outfilename)
	ling_stats = decode_speech(audio_filename)	

        end = time.time()
        total_time =round(end - start)


        stats['time_to_analyze'] = total_time
	print("AUDIO_2!!!: {0}".format(audio_filename))
	stats['total speech time'] = get_duration(audio_filename)
        # combine the different stats to display in the template
        stats = dict(stats.items() + ling_stats.items())
	
	app.logger.warning('stats: {0}'.format(stats))

	# render the speech as text on a different page
        return render_template('decoded_speech.html', stats=stats, video_filename=video_filename, audio_filename=audio_filename)


    # Get the name of the uploaded file
    # file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    #if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
     #   filename = secure_filename(file.filename)

        # Move the file form the temporal folder to
        # the upload folder we setup
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	#filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	#outfilename = '/home/ec2-user/flask_attempts/data/test.txt'
	
	# create a dictionary to pass to the template
	#stats = dict()
	
	
	# decode the speech in the file
#	ling_stats = decode_speech_driver(filename, outfilename)
	
#	end = time.time()
#	total_time =round(end - start)

#	stats['time_to_analyze'] = total_time

	# combine the different stats to display in the template
#	stats = dict(stats.items() + ling_stats.items())

	# render the speech as text on a different page	
#	return render_template('decoded_speech.html', stats=stats)	 	

        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        # return redirect(url_for('uploaded_file',
	#                                filename=filename))


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("80"),
        debug=True
    )

