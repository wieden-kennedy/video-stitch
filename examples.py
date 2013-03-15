from videostitch import stitch, normalize


# clips = [open('test_videos/1.mpg'), open('test_videos/2.mpg')]
# combined = stitch(clips, output="/tmp/sss.mp4")

norm = normalize(open('test_videos/1.mpg'), output='/tmp/ABC.mpg')