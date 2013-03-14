from os.path import join
from cStringIO import StringIO
from sh import ffmpeg, wc, ls
from Queue import Queue

def stitch(videos, output):
	# Feed the video streams using a generator to avoid
	# in-memory concat of all the streams
	def feed():
		for v in videos:
			yield v.read()

	ffmpeg("-q:v", "0", '-vcodec', 'libx264', '-acodec', 'libfaac', output, y=True, i="pipe:0", r=25, _in=feed(), _in_bufsize=1024)
	return open(output, 'r')