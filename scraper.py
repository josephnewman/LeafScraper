from bs4 import BeautifulSoup
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime

import requests, os, time

load_dotenv()

TARGET_URL = 'https://leafstailgate.com/'
TARGET_NUMBER = '+16137123484'
ACCOUNT_SID=os.getenv('ACCOUNT_SID')
AUTH_TOKEN=os.getenv('AUTH_TOKEN')
MESSAGING_SID=os.getenv('MESSAGING_SID')


MESSAGES = {
    True:'Tickets now available for Maple Leaf Square!\nGet them while they last!',
    False:'All tickets have now been snapped up for the next game!'
}

class Scraper:
    def __init__(self):
        self.available = False
        self.s = requests.Session()

    def update(self):
        response = self.s.get(TARGET_URL)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.available = 'display: none' not in soup.find_all('form')[0]['style']

        return self.available


class Notifier:
    def __init__(self):
        self.scraper = Scraper()
        self.client = Client(ACCOUNT_SID, AUTH_TOKEN)
        self.last_status = False

        self.event_log = [] # list of dicts: datetime change, change status
        self.log_event('Server startup...')
    

    def log_event(self, message):
        self.event_log.append({'date':datetime.now().strftime('%d/%m/%Y %H:%M:%S'), 'message':message})

    def update(self):
        new_status = self.scraper.update()
        if  new_status != self.last_status:
            self.client.messages.create(
                messaging_service_sid=MESSAGING_SID,
                to=TARGET_NUMBER,
                body=f'\n{MESSAGES[new_status]}\nhttps://leafstailgate.com',
            )
            self.last_status = new_status
            self.log_event('Available' if new_status else 'Unavailable')
        return new_status


    def refresh_page(self):
        self.update()
        return f'''
        <html>
            <head>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
                <title>LeafScraper</title>
            </head>
            <body style='text-align:center;padding:3%;'>
                <h2 style='padding:2%;font-variant:small-caps;'>Passes currently <u>{'available' if self.last_status else 'unavailable'}</u></h2>
                <table class='table'>
                    <thead class='thead-dark'>
                        <tr>
                            <th>Datetime</th>
                            <th>Event</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f"<tr><td>{x['date']}</td><td>{x['message']}</td></tr>" for x in self.event_log[::-1]])}
                    </tbody>
                </table>
            </body>
        </html>
        
        '''