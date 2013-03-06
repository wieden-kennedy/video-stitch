from videostitch import stitch

clips = [open('test_videos/1.mpg'), open('test_videos/2.mpg')]
stitch(clips, output="/tmp/sss.mpg")