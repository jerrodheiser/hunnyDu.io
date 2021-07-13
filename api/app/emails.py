from threading import Thread
from flask import current_app
from flask import render_template
from flask_mail import Message
from . import mail

# Function to send emails asynchronously.
def send_async_email(app, msg):
    # Pass the provided app context.
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """
        This function makes for easy email generation.
        to is a target email/list of emails,
        subject is the actual subject of the email,
        and the body is a rendered html file or txt if you're barbarian.
        The kwargs are passed to the html file generation.
    """

    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    # Create the thread to send the message.
    thr = Thread(target=send_async_email, args=[app, msg])

    # Start the thread.
    thr.start()
    return thr
