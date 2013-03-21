import re
from os.path import join
from cStringIO import StringIO
from sh import ffmpeg, ffprobe, wc, ls
from Queue import Queue


def _probe(video_file):
    if type(video_file) == file:
        out = ffprobe("pipe:0", _in=feed(), _in_bufsize=1024).stderr
    else:
        out = ffprobe(video_file)
    return out.stderr
        

def normalize(video_file, output):
    """
    Transcode the video to mpeg.
    """
    def feed():
        return video_file.read()

    if type(video_file) == file:
        ffmpeg("-y", "-q:v", "0", output, i="pipe:0", r=25, _in=feed(), _in_bufsize=1024)
    else:
        ffmpeg("-y", "-q:v", "0", output, i=video_file, r=25)
    return open(output, 'r')

def change_frame_rate(video_file, output, fps=24):
    """
    Normalize the frame rate of the input file
    """
    def feed():
        return video_file.read()
    frame_rate = get_frame_rate(video_file)

    if type(video_file) == file:
        ffmpeg("-r", frame_rate, "-i", "pipe:0", "-r", "24", output, _in=feed(), _in_bufsize=1024, y=True)
    else:
        ffmpeg("-r", frame_rate, "-i", output, "-r", "24", output, y=True)
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

    out = _probe(video_file)
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
    """
    Transcode the given file to MPEG
    """
    def feed():
        return video_file.read()
    ffmpeg("-q:v", "0", output, y=True, i="pipe:0", r=25, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')

def to_mp4(video_file, output):
    """
    Transcode the given file to MP4 (H264)
    """
    def feed():
        return video_file.read()
    ffmpeg("-i", "pipe:0", "-sameq", "-vcodec libx264", "-acodec libmp3lame", output, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')

def resize(video_file, output, dimensions=(360,360)):
    """
    Resize the video to the given dimensions
    """
    def feed():
        return video_file.read()
    ffmpeg("-i", "pipe:0", "-s", "%sx%s" % dimensions, output, y=True, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')
    
def stitch(videos, output):
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
    ffmpeg("-q:v", "0", '-vcodec', 'libx264', '-acodec', 'libmp3lame', output, y=True, i="pipe:0", r=25, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')


def stitch_theora(videos, output):
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
    ffmpeg("-q:v", "0", '-vcodec', 'libtheora', '-acodec', 'libvorbis', output, y=True, i="pipe:0", r=25, _in=feed(), _in_bufsize=1024)
    return open(output, 'r')


DEFAULT_PROCESSORS = [
    change_frame_rate,
    crop_square,
    resize
    ]


def process_video(video_file, output, processors=DEFAULT_PROCESSORS):
    """
    Run the processors in the iterable processsors
    """
    current_file = video_file
    def feed():
        current_file.read()
    for function in processors:
        current_file = function(current_file, output)
    return open(output, 'r')
