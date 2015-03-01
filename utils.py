import subprocess
import os
import sys
import traceback

def exception_response(e):
	exc_type, exc_value, exc_traceback = sys.exc_info()
	lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
	log_stuff(lines)
	raise Exception(e)

def log_stuff(stuff_to_write, filename='util_warnings.log'):
	with open(filename, 'a') as f:
		f.write('\n'*3)
		type_of_writable = type(stuff_to_write)
		if type_of_writable is str:
			f.write(stuff_to_write)
		elif type_of_writable is list:
			for line in stuff_to_write:
				f.write(line)
		else:
			try:
				f.write(stuff_to_write)
			except Exception as e:
				exception_response(e)
	f.close()

def new_filename(orig, to_add):
	new = orig.rsplit('.')
	new = new[:-1] + [to_add] + ['.'] + [new[-1]]
	return ''.join(new)

def stereo_to_mono(filename):
	try:
		samp_rate = 16000
		call_str = "/usr/local/bin/sox {0} -r {2} {1} channels 1".format(filename, new_filename(filename, '_mono'), samp_rate)
		log_stuff('call string: {0}'.format(call_str))
		subprocess.call(call_str, shell=True, stderr=subprocess.STDOUT)
	except Exception as e:
		exception_response(e)


def get_duration(wavefile):
    import wave
    framerate = 0
    n_frames = 0
    wavfile = wave.open(wavefile, 'rb')
    n_frames = wavfile.getnframes()
    samprate = wavfile.getframerate()
    duration = n_frames / samprate
    return int(duration)



if __name__ == "__main__":
    stereo_to_mono("/home/ec2-user/flask_attempts/uploads/blob_audio.wav")
