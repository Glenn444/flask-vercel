from flask import Flask
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import  generate_password_hash, check_password_hash
from email.message import EmailMessage
import smtplib
from scholarly import scholarly, ProxyGenerator
import os

load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    os.getenv("USERNAME"): generate_password_hash(os.getenv("PASSWORD")),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route('/')
@auth.login_required
def check_google_scholar():
    pg = ProxyGenerator()
    success = pg.ScraperAPI(os.getenv("SCRAPER_API"))
    scholarly.use_proxy(pg)

    # Function to check if journals or articles from "stratfordjournals.com" exist
    def check_stratford_journals():
        search_query = scholarly.search_pubs('site:stratfordjournals.com')
        publications = [pub for pub in search_query]
        return len(publications) > 0

    # Function to send an email
    def send_email(subject, body):
        EmailAdd = os.getenv("SENDER_EMAIL")
        Pass = os.getenv("SENDER_PASS")

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EmailAdd
        msg['To'] = os.getenv("EMAIL1"), os.getenv("EMAIL2")
        msg.set_content(body)

        with smtplib.SMTP_SSL('smtp.hostinger.com', 465) as smtp:
            smtp.login(EmailAdd, Pass)
            smtp.send_message(msg)

    # Check if journals or articles from "stratfordjournals.com" exist
    if check_stratford_journals():
        send_email("Stratford Journals Found On Google Scholar", "Journals or Articles from stratfordjournals.com have been found on Google Scholar.")
        return "Email sent: Stratford Google Scholar Found"
    else:
        send_email("Stratford Journals Not Found On Google Scholar", "Publications for Stratford Journals Not Found on Google Scholar")
        return "Email sent: Stratford Google Scholar Not Found"

if __name__ == '__main__':
    app.run()
