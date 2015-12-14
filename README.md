# Overview
This package creates an API webhook to accept inbound mail requests processed by Postmark (www.postmarkapp.com).

Inbound mail is received from Postmark as JSON, serialized and saved to the database. A Django signal is broadcast with every new email received, allowing your own application to respond to incoming emails.

# Requirements

* Django (1.8, 1.9)
* Django Rest Framework (3.3)
* Python-Dateutil (2.4.2)
* Python-Magic (0.4.10)

# Installation

Install using `pip`...

    pip install django-postmark-inbound

Add `'rest_framework'` and `'postmark_inbound'` to your `INSTALLED_APPS` setting.

    INSTALLED_APPS = (
        ...
        'rest_framework',
        'postmark_inbound',
    )

Remember to use `makemigrations` to create the database schema used by django-postmark-inbound.

    python manage.py makemigrations postmark_inbound

# Example

Create a new project:

    pip install django
    pip install django-postmark-inbound
    django-admin.py startproject postmark_inbound_demo

Add `'rest_framework'` and `'postmark_inbound'` to your `INSTALLED_APPS` setting. See the installation instructions above.

    cd postmark_inbound_demo
    python manage.py makemigrations postmark_inbound
    python manage.py migrate

Edit `urls.py` and create a URL endpoint for our Postmark webhook:

    from django.conf.urls import url, include
    from django.contrib import admin


    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'^postmark/', include('postmark_inbound.urls')),
    ]

Run the development server...

    python manage.py runserver

By default the endpoint is `inbound`, therefore the inbound URL for our webhook would be `http://127.0.0.1:8000/postmark/inbound`

Successful submissions from Postmark will return a `202 Accepted` response.

# Inbound mail received signal

You can listen for inbound mails in your own applications by connecting a receiver function to the `inbound_mail_received` signal.

    from postmark_inbound.signals import inbound_mail_received
    
    def my_callback(sender, **kwargs):
      # Expect mail_data and mail_object keyword arguments
      mail_data = kwargs.get('mail_data')
      mail_object = kwargs.get('mail_object')
      count_attachments = mail_object.attachments.count()
      count_headers = mail_object.headers.count()
      print("Email  received!")
    
    inbound_mail_received.connect(my_callback)

Signals contain the validated data from Postmark's API submission and a model instance of `InboundMail`. You can access the to/from/cc/bcc information, headers and attachments from either the validated data or `InboundMail` model manager.

