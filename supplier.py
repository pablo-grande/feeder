import subprocess
from os import walk
from db import Media
from sys import argv


def get_info(filename):
    media_info = {}
    ffprobe = f'ffprobe -i \"{filename}\" -show_entries format=duration:stream=codec_type -v quiet -of compact=nokey=1'
    try:
        result = subprocess.Popen([ffprobe], stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
        output = result.communicate()[0].decode('utf-8')

        # a video has both video and audio codecs separated by line break
        file_data = {'streams': set(), 'duration': 0.0}
        for data in [e for e in output.split('\n') if e]:
            k, v = data.split('|')
            if k == 'stream':
                file_data['streams'].add(v)
            elif k == 'format':
                if v != 'N/A':
                    file_data['duration'] = float(v)

        a_movie = {'audio', 'video'}
        if a_movie.issubset(file_data['streams']) and file_data['duration'] > 0.0:
            media_info['duration'] = file_data['duration']
        return media_info

    except (ValueError, KeyError) as e:
        print(filename, e)


def supply(media_dir):
    """Given a dirname gets all needed information from video files
    and stores it
    """
    results = []

    for root, _, files in walk(media_dir):
        for _file in files:
            full_name = f'{root}/{_file}'
            media_info = get_info(full_name)
            if media_info:
                m = Media(filename=full_name, **media_info)
                m.save()
                results.append(m)

    return results


if __name__ == '__main__':
    if len(argv) == 2:
        supply(argv[1:].pop())

