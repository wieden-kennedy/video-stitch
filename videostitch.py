import re
from os.path import join
from cStringIO import StringIO
from sh import ffmpeg, ffprobe, wc, ls
from Queue import Queue

def normalize(video_file, output):
    """
    Transcode the video to mpeg.
    """
    def feed():
        return video_file.read()
    ffmpeg("-q:v", "0", output, y=True, i="pipe:0", r=25, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')

def normalize_frame_rate(video_file, output, fps=24):
    """
    Normalize the frame rate of the input file
    """
    def feed():
        return video_file.read()
    frame_rate = get_frame_rate(video_file)
    ffmpeg("-r", frame_rate, "-i", "pipe:0", "-r", "24", output, _in=feed(), _in_bufsize=1024, y=True)
    return open(output, 'r')

def get_frame_rate(video_file):
    """
    Get the frame rate of the video_file
    Look out! Uses regex.
    """
    def feed():
        return video_file.read()
    frame_rate = 0
    pattern = re.compile(r'([0-9]{1,2}(\.[0-9]{1,2})?) fps')
    out = ffprobe("pipe:0", _in=feed(), _in_bufsize=1024).stderr
    print out
    matches = pattern.search(out)
    if matches:
        try:            
            frame_rate = float(matches.groups()[0])
        except IndexError:
            pass
    video_file.seek(0)
    return frame_rate

def get_dimensions(video_file):
    """
    Get the dimensions of the video.
    Look out! Uses regex.
    """
    width = height = 0
    def feed():
        return video_file.read()
    pattern = re.compile(r'([0-9]{3,4})x([0-9]{3,4}),')
    out = ffprobe("pipe:0", _in=feed(), _in_bufsize=1024).stderr
    matches = pattern.search(out)
    if matches:
        width, height = map(int, matches.groups()[0:2])
    video_file.seek(0)
    return width, height

def crop_square(video_file, output):
    """
    Crop the video into a square shape
    """
    dimensions = get_dimensions(video_file)
    smallest = min(dimensions)
    return crop(video_file, (smallest, smallest), output)

def crop(video_file, dimensions, output, origin=(0,0)):
    """
    Crop the given video from the top left corner
    to the given dimensions.
    """
    def feed():
        return video_file.read()
    format = dimensions + origin
    ffmpeg("-i", "pipe:0", "-filter:v", "crop=%s:%s:%s:%s" % format , output, y=True, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')

def to_theora(video_file, output):
    """
    Convert the given video file to theora
    """
    def feed():
        return video_file.read()
    ffmpeg("-i", "pipe:0",  "-vcodec", "libtheora", "-acodec",  "libvorbis", output, _in=feed(), _in_bufisize=1024)
    return open(output, "r")

def to_mpeg(video_file, output):
    def feed():
        return video_file.read()
    ffmpeg("-q:v", "0", output, y=True, i="pipe:0", r=25, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')
    
def stitch(videos, output):
    # Feed the video streams using a generator to avoid
    # in-memory concat of all the streams
    def feed():
        for v in videos:
            yield v.read()
    ffmpeg("-q:v", "0", '-vcodec', 'libx264', '-acodec', 'libmp3lame', output, y=True, i="pipe:0", r=25, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')
