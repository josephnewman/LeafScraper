from flask import Flask

import scraper

LOG_NAME = 'status.log'
NOTIFIER = scraper.Notifier()
app = Flask(__name__)

@app.route('/')
def home():
    return NOTIFIER.refresh_page()


if __name__ == '__main__':
    app.run(
        '0.0.0.0'
    )