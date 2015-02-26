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
from decode_speech import decode_speech_driver


# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'wav'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():

    # let's time it
    start = time.time()

    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)

        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	outfilename = '/home/ec2-user/flask_attempts/data/test.txt'
	
	# create a dictionary to pass to the template
	stats = dict()
	
	
	# decode the speech in the file
	ling_stats = decode_speech_driver(filename, outfilename)
	
	end = time.time()
	total_time =round(end - start)

	stats['time_to_analyze'] = total_time

	# combine the different stats to display in the template
	stats = dict(stats.items() + ling_stats.items())

	# render the speech as text on a different page	
	return render_template('decoded_speech.html', stats=stats)	 	

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

