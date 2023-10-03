import requests

addr = 'http://mailer.default.127.0.0.1.sslip.io'
post_url = addr + '/'

with (open('Original-standard-test-image-of-Mandrill-also-known-as-Baboon.png', 'rb')) as file:
    post_file = {'file': file}
    response = requests.post(post_url, files=post_file)
    print(response.text)
