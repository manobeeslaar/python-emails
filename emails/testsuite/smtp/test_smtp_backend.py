# encoding: utf-8
from __future__ import unicode_literals
import os
import logging
import pytest
import emails
from emails.backend.smtp import SMTPBackend


TRAVIS_CI = os.environ.get('TRAVIS')
HAS_INTERNET_CONNECTION = not TRAVIS_CI

SAMPLE_MESSAGE = {'html': '<p>Test from python-emails',
                  'mail_from': 's@lavr.me',
                  'mail_to': 'sergei-nko@yandex.ru',
                  'subject': 'Test from python-emails'}


def test_send_to_unknown_host():
    server = SMTPBackend(host='invalid-server.invalid-domain-42.com', port=25)
    response = server.sendmail(to_addrs='s@lavr.me', from_addr='s@lavr.me', msg=emails.html(**SAMPLE_MESSAGE))
    server.close()
    assert response.status_code is None
    assert response.error is not None
    assert isinstance(response.error, IOError)
    assert not response.success
    print("response.error.errno=", response.error.errno)
    if HAS_INTERNET_CONNECTION:
        # IOError: [Errno 8] nodename nor servname provided, or not known
        assert response.error.errno == 8


def test_smtp_reconnect(smtp_server):

    # Simulate server disconnection
    # Check that SMTPBackend will reconnect

    server = SMTPBackend(host=smtp_server.host, port=smtp_server.port, debug=1)
    client = server.get_client()
    logging.debug('simulate socket disconnect')
    client.sock.close()  # simulate disconnect
    response = server.sendmail(to_addrs='s@lavr.me',
                               from_addr='s@lavr.me',
                               msg=emails.html(**SAMPLE_MESSAGE))
    server.close()
    assert response.success
    print(response)


def test_smtp_init_error(smtp_server):

    # test error when ssl and tls arguments both set
    with pytest.raises(ValueError):
        SMTPBackend(host=smtp_server.host,
                     port=smtp_server.port,
                     debug=1,
                     ssl=True,
                     tls=True)


def test_smtp_empty_sendmail(smtp_server):
    server = SMTPBackend(host=smtp_server.host,
                         port=smtp_server.port,
                         debug=1)
    response = server.sendmail(to_addrs=[], from_addr='a@b.com', msg='')
    assert not response

def test_smtp_dict1(smtp_server):
    response = emails.html(**SAMPLE_MESSAGE).send(smtp=smtp_server.as_dict())
    print(response)
    assert response.status_code == 250
    assert response.success


def test_smtp_dict2(smtp_server_with_auth):
    response = emails.html(**SAMPLE_MESSAGE).send(smtp=smtp_server_with_auth.as_dict())
    print(response)
    assert response.status_code == 250
    assert response.success

def test_smtp_dict2(smtp_server_with_ssl):
    smtp = smtp_server_with_ssl.as_dict()
    message = emails.html(**SAMPLE_MESSAGE)
    response = message.send(smtp=smtp)
    print(response)
    assert response.status_code == 250
    assert response.success
    message.smtp_pool[smtp].get_client().quit()
