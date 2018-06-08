Payment system
==============

This page gives an overview of how the payments are processed.

How is the processing triggered?
--------------------------------

We use `Celery <http://www.celeryproject.org/>`_ to download and process payment files in regular time intervals. The Celery tasks are defined in :code:`tq_website/tasks.py`.
The following Celery tasks are responsible for the payment system:
- Task to download the new transactions from PostFinance.
- Task to parse the downloaded transactions and insert them into the database.
- Task to process payments.

How and where are the transactions stored?
------------------------------------------

- The information about the transactions are stored on an SFTP server maintained by PostFinance.
- The data format is called `ISO 20022 <https://www.six-interbank-clearing.com/dam/downloads/en/standardization/iso/swiss-recommendations/implementation-guidelines-camt.pdf>`_. It is XML based. The pages 37-43 describe the XML attributes: Use this e. g. to see what information is stored and how it can be accessed.
- The downloaded files are saved in :code:`BASE_DIR/FDS_DATA_PATH`, where :code:`BASE_DIR` and :code:`FDS_DATA_PATH` are stored inside :code:`tq_website/settings.py`. (:code:`BASE_DIR` is the project root directory, :code:`FDS_DATA_PATH = 'fds_data'`)
- Processed files are marked by appending :code:`.processed` to the filename.

What does "process payments" mean?
----------------------------------

When a payment is said to be "processed", it means that the system tries to relate ("match") a payment to a course subscription. If the subscription cannot be successfully matched and/or the paid amount is not correct, human intervention is needed. This is indicated by setting the payment status to :code:`MANUAL`.

What does it mean if a payment is marked as :code:`MANUAL`?
-----------------------------------------------------------

A payment can be marked for manual processing if in one of the following cases:

- The payment cannot be related ("matched") to a course subscription.
- The paid amount is not enough to pay the subscription.
- The paid amount is higher than the subscription cost.

High level procedure
--------------------
First, the payments are fetched and saved. Involved files:

- The payments to our bank account are fetched from an SFTP server from PostFinance.
- The XML files are parsed and for each transaction, a Payment object is inserted into the database. (The Payments have state :code:`NEW` at this point.) Afterwards, the XML file is marked as processed.
- The following operations are applied to new payments: Debit transactions (money that goes out of our account) are marked as :code:`IRRELEVANT`. Process the credit transactions (money comes into our account) in the following way: If something goes wrong while processing a payment, set the payment state to :code:`MANUAL`. If the payment can be successfully matched to a course subscription, a SubscriptionPayment is created and stored in the database. Then, the payment status is changed: If the payed amount is equal to the amount that is to be paid, the state of the Payment object is set to :code:`MATCHED`. If the payed amount is not enough or too much, the state of the Payment object is set to :code:`MANUAL`.

  Finally, all :code:`MATCHED` payments are marked as paid and :code:`PROCESSED`.
- In all cases where a subscription is marked as paid, an "online payment successful" email is sent to the user.

Which files are involved?
-------------------------

- :code:`tq_website/tasks.py`: contains the Celery tasks
- :code:`payments/postfinance_connector.py`: Contains code to download XML files from a PostFinance SFTP server and extract payments from them
- :code:`payments/payment_processor.py`: Contains code to process the new payments.
- :code:`payments/models.py`: Contains the classes related to payments (especially :code:`Payment` and :code:`SubscriptionPayment`)
