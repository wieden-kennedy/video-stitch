video-stitch
============

Stitch multiple video files together using an easy, high-level API

### Usage

A simple example, reading videos from disk

```
from videostitch import stitch

# A list of file-like objects (currently, only read() needs to be implemented)
videos = [open('clip_1.mp4'), open('clip_2.mp4')]

stitch(videos, output='combined.mp4')
```

An example where the videos are stored in Redis

```
from videostitch import stitch

class RedisVideo:
  def __init__(self, key):
    self.client = StrictRedis()
    self.key = key
    
  def read(self):
    return self.client.get(self.key)

videos = [RedisVideo('videos:16fh0387083'), RedisVideo('videos:c0331730ug02')]

combined = stitch(videos) # Omit the output kwarg to return a file descriptor

print combined # print stitched video to stdout


```

Installation
============

Make sure you have `exittool` installed.

```
sudo apt-get install libimage-exiftool-perl
````