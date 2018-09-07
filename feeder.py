from flask import Flask, render_template
from datetime import datetime
from db import Episode, now


application = Flask(__name__)


@application.route("/")
def random_tv():
    episode = Episode.pick()
    context = {}

    offset = (now() - episode.scheduled).total_seconds()
    if offset > 0:
        if offset < episode.duration:
            context['offset'] = offset
        else:
            episode = episode.next()
            offset = (now() - episode.scheduled).total_seconds()
            context['wait'] = offset
    else:
        context['wait'] = abs(offset)

    context['episode'] = episode
    return render_template("index.html", context=context)


if __name__ == '__main__':
    application.run(host='0.0.0.0')

