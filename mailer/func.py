from parliament import Context
from flask import Request
import smtplib, ssl
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import json


send_to = ['jmdeleonpi@gmail.com']  

def compose_message(sender : str, send_to : list, report_name : str, file_obj):

    message = f'Imagenes procesadas:\n'

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = f'Procesamiento de imagenes'
    msg.attach(MIMEText(message))


    part = MIMEBase('application', 'octet-stream')
    part.set_payload(file_obj.read())

    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    f'attachment; filename={Path(report_name).name}')
    msg.attach(part)

    return msg

def send_message(credentials : dict, send_to : list, msg):
    try:
        server_name = "smtp.gmail.com"
        port = 587  # For starttls
        context = ssl.create_default_context()
        smtp_server = smtplib.SMTP(server_name, port)
        smtp_server.ehlo() # Can be omitted
        smtp_server.starttls(context=context) # TLS
        smtp_server.ehlo() # Can be omitted
        smtp_server.login(credentials['mail'], credentials['password'])
        smtp_server.sendmail(credentials['mail'], send_to, msg.as_string())

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        smtp_server.quit() 



# parse request body, json data or URL query parameters
def payload_print(request: Request) -> str:

    with open(f'credentials.json', 'r') as f:
        creds = json.loads(f.read())
    
    if request.method == 'POST':

        file = request.files['file']

        #compose e-mail
        msg = compose_message(creds['mail'], send_to, f'foo.png', file)
        send_message(creds, send_to, msg)
        
        #Responder "OK!""
        return f'''<html>

                <H1>Mail sent to {send_to}!</H1>

                </html>'''

    elif request.method == "GET":
        return '''
        <!doctype html>
        <title>Welcome!</title>
        <h1>This service sends mails with the files sent to it in an HTTP POST attached.</h1>
        '''


# pretty print the request to stdout instantaneously
def pretty_print(req: Request) -> str:
    ret = str(req.method) + ' ' + str(req.url) + ' ' + str(req.host) + '\n'
    for (header, values) in req.headers:
        ret += "  " + str(header) + ": " + values + '\n'

    if req.method == "POST":
        ret += "Request body:\n"
        ret += "  " + payload_print(req) + '\n'

    elif req.method == "GET":
        ret += "URL Query String:\n"
        ret += "  " + payload_print(req) + '\n'

    return ret

 
def main(context: Context):
    """ 
    Function template
    The context parameter contains the Flask request object and any
    CloudEvent received with the request.
    """

    # Add your business logic here
    print("Received request")

    if 'request' in context.keys():
        ret = pretty_print(context.request)
        print(ret, flush=True)
        return payload_print(context.request), 200
    else:
        print("Empty request", flush=True)
        return "{}", 200
