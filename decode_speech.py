"""
file: decode_speech.py
source: http://stackoverflow.com/questions/14307816/live-recognition-with-python-and-pocketsphinx


"""

import sys
import os
import subprocess


try:
    user_paths = os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
except KeyError:
    user_paths = []

print(user_paths)

def decode_speech(hmm, lm, dic, wavfile):
    """
    Decodes a speech file
    """
    try:
        import pocketsphinx as ps
        import sphinxbase
    except:
	print """Pocketsphinx and sphixbase is not installed
        in your system. Please install it with package manager.
	"""
	return ("Something went wrong","")

    sample_rate = '16000'
    speechRec = ps.Decoder(hmm=hmm, lm=lm, dict=dic, samprate=sample_rate)
    #speechRec = ps.Decoder(hmm=hmm, lm=lm, dict=dic)
    wavFile = file(wavfile,'rb')
    wavFile.seek(100)
    speechRec.decode_raw(wavFile)
    result = speechRec.get_hyp()
    return result

def analyze_response(response):
    """
    Analyzes the response
    """
    try:
        import nltk
    except Exception as e:
        print("nltk is not installed on your system.")
        raise Exception(e)	

    if type(response) is not str:
	print(response)
	print("actual type: {0}".format(type(response)))
        raise Exception("input not a string")

    # create dictionary to collect the stats
    ling_stats = dict()

    tokens = nltk.word_tokenize(response)
    freq_dist = nltk.FreqDist(tokens)
    print('most common single word: {0}'.format(freq_dist.most_common(1)))
    bigrams = list(nltk.bigrams(tokens))
    freq_dist_biagrams = nltk.FreqDist(bigrams)
    print('most common bigram: {0}'.format(freq_dist_biagrams.most_common(1)))
    #collocations = nltk.collocations(tokens)
    #print('collocations: {0}'.format(collocations))
    freq_dist_word_lengths = nltk.FreqDist(len(w) for w in tokens)
    print('frequency distribution of word lengths: {0}'.format(freq_dist_word_lengths.most_common(1)))
    ling_stats['most common single word'] = freq_dist.most_common(1)
    ling_stats['most frequent bigram'] = freq_dist_biagrams.most_common(1) 
    ling_stats['frequency distribution of word lengths'] = freq_dist_word_lengths.most_common(1) 
    ling_stats['number of time you said the word I'] = tokens.count('i') 

    return ling_stats

def decode_speech_driver(wavfile, outfile):
    
    
    hmm = '/home/ec2-user/download/cmusphinx-5prealpha-en-us-2.0'
    lm = "/home/ec2-user/download/cmusphinx-5.0-en-us.lm.dmp"
    dic = "/home/ec2-user/download/pocketsphinx-0.8/model/lm/en_US/hub4.5000.dic"
    samprate = 16000
    try:
        call_str = "/usr/local/bin/pocketsphinx_continuous -infile {0} -samprate {1} -lm {2} -hmm {3} -dict {4} > {5}".format(wavfile, samprate, lm, hmm, dic, outfile)
        NULL = open(os.devnull, 'w')    # add:  stdout=FNULL    when it works
        subprocess.call(call_str, shell=True, stderr=subprocess.STDOUT)
    except Exception as e:
        print("Something went wrong")
        print(e)

    with open(outfile, 'rb') as speech_file:
	speech = ''.join(speech_file.readlines())
	ling_stats = analyze_response(speech)
	rtn_dict = dict()
	rtn_dict['speech'] = speech
	return dict(rtn_dict.items() + ling_stats.items())


if __name__ == "__main__":
    #hmm = "/home/ec2-user/download/pocketsphinx-0.8/model/hmm/en_US/hub4wsj_sc_8k"
    hmm = '/home/ec2-user/download/cmusphinx-5prealpha-en-us-2.0'
    lm = "/home/ec2-user/download/cmusphinx-5.0-en-us.lm.dmp"
    dic = "/home/ec2-user/download/pocketsphinx-0.8/model/lm/en_US/hub4.5000.dic"
    wavfile = "/home/ec2-user/data/test.wav"
    result = decode_speech(hmm,lm,dic,wavfile)
    print('\nresult: {0}\n'.format(result))
    analyze_response(result[0])

