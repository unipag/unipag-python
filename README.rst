Unipag Client for Python
========================

.. image:: https://travis-ci.org/unipag/unipag-python.png?branch=master
        :target: https://travis-ci.org/unipag/unipag-python

Requirements
------------

Python version 2.6 or 2.7, or PyPy. For better security, we recommend to
install `Python Requests`_ library, since it supports SSL certs verification.
To install Requests, simply run: ::

    $ pip install requests

or using easy_install: ::

    $ easy_install requests

Requests library is optional. If it is not installed, Unipag Client will use
urllib2 instead. All features of Unipag Client will remain fully functional, but
it will not verify SSL certificate of Unipag API.

.. _`Python Requests`: http://docs.python-requests.org/

Installation
------------

Install using pip, recommended (`why?`_): ::

    $ pip install unipag

or using easy_install: ::

    $ easy_install unipag

.. _`why?`: http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install

Sample usage
------------

Create invoice
~~~~~~~~~~~~~~

.. code:: python

    import unipag
    import unipag.defaults

    # Get your key at https://my.unipag.com
    unipag.defaults.api_key = '<your-secret-key>'

    invoice = unipag.Invoice.create(
        amount=42,
        currency='USD'
    )

    # Done. invoice.id now contains unique id of this invoice at Unipag.

Install Unipag widget
~~~~~~~~~~~~~~~~~~~~~

Try our widget for payments workflow handling. It's quite optional, but you
might find it handy and time-saving.

.. code:: html

    <script type="text/javascript"
        src="//d3oe3cumn3db7.cloudfront.net/uw3/js/uw3.min.js"
        charset="utf-8"
        id="uw3js"
        data-key="<your-public-key>">
    </script>

Please note, it is important that you use **public key** for widget.
Public keys have restricted access to your data and are supposed to be safe
for use in browser.


Handle webhook from Unipag
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a standalone page on your website which will handle events sent by
Unipag. Register URL of this page at `<https://my.unipag.com>`_ > Settings > Webhooks.
Initialize page code as following (example for Django):

.. code:: python

    import unipag
    import unipag.defaults
    from django.http import HttpResponse, HttpResponseBadRequest

    # Get your key at https://my.unipag.com
    unipag.defaults.api_key = '<your-secret-key>'


    def handle_unipag_hook(request):
        """
        An example of Django view for handling hooks from Unipag.
        """
        event = unipag.objects_from_json(request.body)

        # Unipag should send correctly constructed event objects
        if not isinstance(event, unipag.Event):
            return HttpResponseBadRequest('Bad request')

        # In this example we subscribe to invoice-related events only
        if isinstance(event.related_object, unipag.Invoice):

            # Always reload information from Unipag for security reasons:
            invoice = event.related_object.reload()

            # Now invoice object contains the most recent information,
            # securely loaded from Unipag.

            # ... do something with invoice data ...

        # Return HTTP 200 to let Unipag know that we successfully received message
        return HttpResponse('OK')

Tip: webhooks can be a pain to debug. Check out Unipag Network Activity log, it
is available at `<https://my.unipag.com>`_ > Network Activity. You may find it
useful for your webhook handlers debugging.

Usage of invoice "custom_data" property
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Invoice objects have an optional "custom_data" property, which can be used to
store up to 32KB of arbitrary data in JSON format. You can freely use this field
to store additional information about invoices, which is specific for your
application.

In Python, you can use dicts, lists, strings, numbers, boolean and None values
in any combination to store them in custom_data. All of these types will be
properly serialized when sending to Unipag and deserialized when fetching them
back. Consider the following examples, all of them are valid usages of
custom_data property:

.. code:: python

    import unipag
    import unipag.defaults

    # Get your key at https://my.unipag.com
    unipag.defaults.api_key = '<your-secret-key>'

    invoice = unipag.Invoice.create(
        amount=42,
        currency='USD'
    )

    # Store dicts, lists and single values
    invoice.custom_data = {
        'address': {
            'billing': '5863 Gentle Pond Rise, Suspension, Ontario, CA',
            'shipping': '9215 Red Ridge, Lancer, Idaho, US',
        },
        'contact_phones': ['555-4242', '555-9000'],
        'magic_number': 42,
    }
    invoice.save()

    # Clean everything out
    invoice.custom_data = None
    invoice.save()

    # Store a single value. Yes, it will be a valid JSON.
    invoice.custom_data = True
    invoice.save()

    # Store list as a root element. Let's assume that we need to save cart items:
    invoice.custom_data = [
        {
            "product": "apples",
            "price": 10.0,
            "quantity": 1
        },
        {
            "product": "oranges",
            "price": 12.5,
            "quantity": 2
        }
    ]
    invoice.save()


Report bugs
-----------

Report issues to the project's `Issues Tracking`_ on Github.

.. _`Issues Tracking`: https://github.com/unipag/unipag-python/issues
