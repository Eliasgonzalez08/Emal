#!/usr/bin/env python
# coding: utf-8

# # P1
# 

# In[2]:


import getpass, poplib
import smtplib, ssl #smtp
import json

from ssl import Purpose #smtp
from getpass import getpass #smto
from bs4 import BeautifulSoup
from db import crear_conexion
from smtp import user_smtp, smtp

from exchangelib import Credentials, Account, Configuration, DELEGATE, FileAttachment
from exchangelib.folders import Messages

from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from psycopg2 import connect #BD
from psycopg2.extras import RealDictCursor #BD


# ### correo / smtp
# Datos extraidos de carperta correos, se encripta el mensaje con el starttls

# In[3]:


user_smtp = "despprueba@cofepris.gob.mx"
password_smtp = 'c1t4$003'
context = ssl.create_default_context()
smtp = smtplib.SMTP(  host= "mail.cofepris.gob.mx", port= 587 )
smtp.starttls( context = context )
smtp.login( user_smtp, password_smtp)


# try:
#     user_smtp = "despprueba@cofepris.gob.mx"
#     password_smtp = 'c1t4$003'
#     context = ssl.create_default_context()
#     smtp = smtplib.SMTP(  host= "mail.cofepris.gob.mx", port= 587 )
#     smtp.starttls( context = context )
#     smtp.login( user_smtp, password_smtp)
# except Exception as e:
#     raise Exception("Ha ocurrido un error al iniciar sesión en el SMTP ", e, type( e ) )

# ### correo / db
# se crea una conexión con la base de datos posgresSQL

# In[6]:


PROD_DB = {
    "user": "postgres", 
    "password": "",
    "host": "192.168.253.83",
    "database": "zammad",
    "cursor_factory": RealDictCursor
}

# Creamos una funcion que nos devuelve la conexion
def crear_conexion():
    return connect( **PROD_DB )

conexion=crear_conexion()
print(conexion)


# ### correo / app

# In[52]:


DESTINATARIO_PRUEBA="Eliasgonzalezaguila08@gmail.com"
credential = Credentials( "despprueba@cofepris.gob.mx", "c1t4$003")
configuration = Configuration( server = 'mail.cofepris.gob.mx', credentials=credential )
account = Account('despprueba@cofepris.gob.mx', config=configuration, autodiscover= False, access_type=DELEGATE)
#print("Recorriendo lista de correos...")
messagesIdTemp = []
for item in account.inbox.all().order_by('-datetime_received'):
    subject = item.subject
    cc: list = [] if not item.cc_recipients else [ i.email_address for i in item.cc_recipients ]
    to = item.sender.email_address
    print(to)
    #recipients = [ i.email_address  for i in item.to_recipients if i.email_address != 'despprueba@cofepris.gob.mx' ]
    fecha_recibido = item.datetime_received.strftime("%Y-%m-%d %H:%M:%S")
    print(fecha_recibido)
    body = BeautifulSoup( item.body, "html.parser" )
    to_html = body.new_tag("p")
    to_html.string = f"Enviado por: {to}"
    to_cc_html = body.new_tag("p")
    to_cc_html.string = "Con copia para: " + ", ".join( cc )
    to_recipients_html = body.new_tag("p")
    to_recipients_html.string = "Enviado tambien a: " + ", ".join( recipients )
    body.html.body.append( to_html )
    body.html.body.append( to_cc_html )
    body.html.body.append( to_recipients_html )
    body = body.prettify(encoding='utf-8').decode('utf-8')
    messagesIdTemp.append( { "message_id": item.message_id, 
                        "subject": subject, 
                        "cc": cc, "to": to, 
                        "recipients": recipients, 
                        "adjuntos": adjuntos, 
                        "body": body ,
                        "fecha_recibido": fecha_recibido ,"type": "Inbox" } )


# In[53]:


messagesIdTemp


# In[38]:


body = BeautifulSoup( item.body, "html.parser" )
to_html = body.new_tag("p")
to_html.string = f"Enviado por: {to}"
to_cc_html = body.new_tag("p")
to_cc_html.string = "Con copia para: " + ", ".join( cc )
to_recipients_html = body.new_tag("p")
to_recipients_html.string = "Enviado tambien a: " + ", ".join( recipients )
body.html.body.append( to_html )
body.html.body.append( to_cc_html )
body.html.body.append( to_recipients_html )
body = body.prettify(encoding='utf-8').decode('utf-8')
messagesIdTemp.append( { "message_id": item.message_id, 
                        "subject": subject, 
                        "cc": cc, "to": to, 
                        "recipients": recipients, 
                        "adjuntos": adjuntos, 
                        "body": body ,
                        "fecha_recibido": fecha_recibido ,"type": "Inbox" } )


# In[39]:


body


# In[40]:


messagesIdTemp


# In[54]:


mensajes = sorted( messagesIdTemp, key= lambda i: i["fecha_recibido"] )
print(mensajes)


# In[ ]:


########### se estable la concexion con 
try:
    user_smtp = "despprueba@cofepris.gob.mx"
    password_smtp = 'c1t4$003'
    context = ssl.create_default_context()
    smtp = smtplib.SMTP(  host= "mail.cofepris.gob.mx", port= 587 )
    smtp.starttls( context = context )
    smtp.login( user_smtp, password_smtp)
except Exception as e:
    raise Exception("Ha ocurrido un error al iniciar sesión en el SMTP ", e, type( e ) )


# In[70]:


DESTINATARIO_PRUEBA='egonzaleza@cofepris.gob.mx'

conexion = crear_conexion()
cursor = conexion.cursor()
sql_zammad = "SELECT 1 FROM ticket_articles WHERE message_id = %s"
for i in mensajes:
    mensaje_id = i.get('message_id')
    cursor.execute( sql_zammad, ( mensaje_id, ) )
    resultado = cursor.fetchall()
    if len(resultado)<=0:
        if not i.get("adjuntos"):
            msg = MIMEMultipart()
            msg["Subject"] = i.get("subject")
            print(i.get("subject"))
            msg["From"] = user_smtp
            print(user_smtp)
            msg["To"] = DESTINATARIO_PRUEBA
            print(msg["To"])
            msg["message_id"] = item.message_id
            print(item.message_id)
            body = MIMEText( i.get("body"), 'html', 'utf-8' )
            msg.attach( body )
            print('.'*20)
            smtp.sendmail( msg["From"], msg["To"], msg.as_string() )
            print("Mensaje enviado correctamente")
        else: 
            print('mensaje con adjuntos no leido')
    else:
        print('Mensaje ya existe')


# In[60]:


msg = MIMEMultipart()
msg["Subject"] = i.get("subject")
msg["From"] = user_smtp
msg["To"] = DESTINATARIO_PRUEBA
msg["message_id"] = item.message_id
body = MIMEText( i.get("body"), 'html', 'utf-8' )
msg.attach( body )
smtp.sendmail( msg["From"], msg["To"], msg.as_string() )


# In[ ]:





# In[ ]:





# ### PopSalud py

# In[29]:


M = poplib.POP3_SSL( host= "owa.salud.gob.mx", port= 995 )
M.user( "sigc@salud.gob.mx" )
M.pass_( "ZenCyt_#mix1" )
numMessages = len(M.list()[1])
print("Numero de mensajes: ", numMessages  )


# In[66]:


try:
    user_smtp = "despprueba@cofepris.gob.mx"
    password_smtp = 'c1t4$003'
    context = ssl.create_default_context()
    smtp = smtplib.SMTP(  host= "mail.cofepris.gob.mx", port= 587 )
    smtp.starttls( context = context )
    smtp.login( user_smtp, password_smtp)
except Exception as e:
    raise Exception("Ha ocurrido un error al iniciar sesión en el SMTP ", e, type( e ) )


# In[ ]:





# In[8]:


from exchangelib import Credentials, Account, Configuration, DELEGATE, FileAttachment
import smtplib
import json
from bs4 import BeautifulSoup
from smtp import user_smtp, smtp
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from exchangelib.folders import Messages
from db import crear_conexion


# In[5]:


get_ipython().system('pip install psycopg2')


# In[ ]:




