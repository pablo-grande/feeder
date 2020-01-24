from bottle import get, run, template, static_file
from datetime import datetime
from db import Media, now


@get('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static/')


@get("/")
def random_tv():
    episode = Media.pick()
    context = {
        'episode': episode.filename,
        'wait': 0.0,
        'offset': 0.0
    }

    if episode.scheduled:
        time_diff = abs(int((now() - episode.scheduled).total_seconds()))
        if time_diff < episode.duration:
            context['offset'] = time_diff
        else:
            context['wait'] = time_diff

    return template("templates/index.html", context=context)


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)

