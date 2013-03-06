from os.path import join
from cStringIO import StringIO
from sh import ffmpeg, wc, ls

def stitch(videos, output):
	_in = ''
	for v in videos:
		_in += v.read()

	ffmpeg("-q:v", "0", output, y=True, i="pipe:0", r=25, _in=_in, _in_bufsize=1024)