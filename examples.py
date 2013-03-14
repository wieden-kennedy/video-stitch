from videostitch import stitch


clips = [open('test_videos/1.mpg'), open('test_videos/2.mpg')]
combined = stitch(clips, output="/tmp/sss.mp4")
# combined is  file descriptor