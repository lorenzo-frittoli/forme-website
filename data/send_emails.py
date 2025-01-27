import smtplib, ssl
from email.mime.text import MIMEText

BLOCK = 50

sender = input("SENDER:: ")
password = input("TOKEN:: ")

subject = "Credenziali di accesso: prenotazioni ForMe"
with open("email_template.txt", "r") as inF:
    body = inF.read()

print(sender, password)

with open("passwords.txt", "r") as in_file:
    student_credentials = list(map(str.split, in_file.readlines()))

print(
    '\n'.join(
        "-> " + line for line in body.format(email=student_credentials[0][0], password=student_credentials[0][1]).split('\n')
    )
)

if input("CONTINUE? Y/n:: ") != 'Y':
    exit(0)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
    # smtp_server.starttls(context=ssl.create_default_context()) # smtplib.SMTP() on port 587 / 25
    smtp_server.login(sender, password)
    for idx, (student_email, student_pwd) in enumerate(student_credentials):
        msg = MIMEText(body.format(email=student_email, password=student_pwd))
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = student_email
        smtp_server.sendmail(sender, student_email, msg.as_string())
        print(student_email)
        # Reset the connection every BLOCK emails
        if idx % BLOCK == BLOCK-1:
            smtp_server.rset()
