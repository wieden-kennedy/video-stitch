import re
import tempfile
from os.path import join
from cStringIO import StringIO
from sh import ffmpeg, ffprobe, wc, ls, avconv
from Queue import Queue

def _probe(video_file):
    if hasattr(video_file, 'read'):
        out = ffprobe("pipe:0", _in=video_file.read(), _in_bufsize=1024).stderr
        video_file.seek(0)
    else:
        out = ffprobe(video_file)
    if len(out) > 0:
        return out
    return out.stderr

def normalize(video_path, output=None):
    """
    Normalize the frame rate of the video at the given path and transcode to mpeg
    """
    if type(video_path) == file:
        video_path = file.name    
    if output is None:
        output = tempfile.NamedTemporaryFile(suffix="stitch.mp4", dir="/tmp/").name
    change_frame_rate(video_path, output)
    tmp = tempfile.NamedTemporaryFile(suffix="stitch.mpeg", dir="/tmp/")
    return to_mpeg(output, tmp.name)

def change_frame_rate(video_file, output, fps=24):
    """
    Normalize the frame rate of the input file
    """
    def feed():
        return video_file.read()
    frame_rate = get_frame_rate(video_file)

    if type(video_file) == file:
        avconv("-y", "-i", "pipe:0", "-strict","experimental", "-vf", "scale=%s:%s" % get_dimensions(video_file.name), "-r", "24", output, _in=feed(), _in_bufsize=1024)
    else:
        avconv("-y", "-i", video_file, "-strict", "experimental", "-vf", "scale=%s:%s" % get_dimensions(video_file), "-r", "24", output)
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

    out = _probe(video_file)
    matches = pattern.search(out)
    if matches:
        try:            
            frame_rate = float(matches.groups()[0])
        except IndexError:
            pass
    
    return frame_rate

def get_dimensions(video_file):
    """
    Get the dimensions of the video.
    Look out! Uses regex.
    """
    width = height = 0
    def feed():
        return video_file.read()
    pattern = re.compile(r'([0-9]{3,4})x([0-9]{3,4})')

    out = _probe(video_file)
    matches = pattern.search(out)
    if matches:
        width, height = map(int, matches.groups()[0:2])
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
    ffmpeg("-y", "-i", "pipe:0", "-vf", "crop=%s:%s:%s:%s" % format, output,  _in=feed(), _in_bufsize=1024)
    return open(output, 'r')

def to_theora(video_file, output):
    """
    Convert the given video file to theora
    """
    def feed():
        return video_file.read()
    ffmpeg("-y", "-i", "pipe:0",  "-vcodec", "libtheora", "-acodec",  "libvorbis", output, _in=feed(), _in_bufsize=1024)
    return open(output, "r")

def to_mpeg(video_file, output):
    """
    Transcode the given file to MPEG
    """
    def feed():
        return video_file.read()

    if type(video_file) == file:
        ffmpeg("-y", "-i", "pipe:0", "-r", 25, output, _in=feed(), _in_bufsize=1024)
    else:
        ffmpeg("-y", "-i", video_file, "-r", 25, output)
    
    return open(output, 'r')

def to_mp4(video_file, output):
    """
    Transcode the given file to MP4 (H264)
    """
    def feed():
        return video_file.read()
    ffmpeg("-y", "-i", "pipe:0", "-sameq", "-vcodec",  "libx264", "-acodec",  "libmp3lame", output, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')

def resize(video_file, output, dimensions=(360,360)):
    """
    Resize the video to the given dimensions
    """
    def feed():
        return video_file.read()
    ffmpeg("-y", "-i", "pipe:0", "-s", "%sx%s" % dimensions, output, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')
    
def stitch(videos, output, vcodec="libx264", acodec="libmp3lame"):
    """
    Stitch together the video files in the iterable 'videos'    
    """
    def feed():
        """
        Feed the video streams using a generator to avoid
        in-memory concat of all the streams
        """
        for v in videos:
            yield v.read()
    ffmpeg("-q:v", "0", '-vcodec', vcodec, '-acodec', acodec, output, y=True, i="pipe:0", r=25, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')

def stitch_to_theora(videos, output):
    return stitch(videos, output, vcodec='libtheora', acodec='libvorbis')

def stitch_to_mp4(videos, output):
    return stitch(videos, output, vcodec="libx264", acodec="libmp3lame")

DEFAULT_PROCESSORS = [
    crop_square,
    resize
    ]


def process_video(video_path, processors=DEFAULT_PROCESSORS):
    """
    Run the processors in the iterable processsors
    """ 
    if type(video_path) == file:
        video_path = file.name
    current_file = normalize(video_path)
    for function in processors:
        output = tempfile.NamedTemporaryFile(suffix="stitch.mpg", dir="/tmp/").name
        old_file = current_file
        current_file = function(current_file, output)
        old_file.close()
    return open(output, 'r')
