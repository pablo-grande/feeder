from flask import Flask, render_template
from datetime import datetime
from db import Media, now


application = Flask(__name__)


@application.route("/")
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

    return render_template("index.html", context=context)


if __name__ == '__main__':
    application.run(host='0.0.0.0')

