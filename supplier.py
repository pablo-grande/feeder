import subprocess
import os
from db import Episode
from sys import exit


def get_length(video):
    #result = subprocess.Popen(['ffprobe -i %s -show_entries format=duration -v quiet -of csv="p=0"' % video], stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
    result = subprocess.Popen(['ffprobe -i \"{}\" -show_entries format=duration -v quiet -of csv="p=0"'.format(video)], stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
    output = result.communicate()
    return float(output[0])


def get_episode_info(filename):
    episode_info = {}
    try:
        episode_info['duration'] = get_length(filename)
    except ValueError as e:
        print(e, filename)
    episode_info['tvshow'] = filename.split('/')[-2]
    return episode_info


def supply(path):
    """Given a dirname gets all needed information from video files
    and stores it
    """
    if os.path.isfile(path):
        e = Episode(episode, **get_episode_info(path))
        e.save()
        
    results = []
    for root, _, episodes in os.walk(path):
        for episode in episodes:
            e = Episode(episode, **get_episode_info(root + '/' + episode))
            e.save()
            results.append(e)

    return results


