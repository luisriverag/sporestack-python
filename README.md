Python library for http://sporestack.com/

# Installation

* `pip install sporestack`

# In action

[![asciicast](https://asciinema.org/a/98672.png)](https://asciinema.org/a/98672)

# Usage

Spawn one and SSH into it.

```
nodemeup
```

Spawn one from your terminal, full Python example.

```
import sporestack
from uuid import uuid4 as random_uuid

node_uuid = str(random_uuid())

ssh_key_path = '{}/.ssh/id_rsa.pub'.format(os.getenv('HOME'))

with open(ssh_key_path) as ssh_key_file:
    sshkey = ssh_key_file.read()

while True:
    node = sporestack.node(days=28,
                           sshkey=sshkey,
                           unique=node_uuid)
    if node.payment_status is False:
        amount = "{0:.8f}".format(node.satoshis *
                                  0.00000001)
        uri = 'bitcoin:{}?amount={}'.format(node.address, amount)
        qr = pyqrcode.create(uri)
        print(qr.terminal())
        print(uri)
        print('Pay with Bitcoin. Resize your terminal if QR code is unclear.')
    else:
        print('Node being built...')
    if node.creation_status is True:
        break
    sleep(5)

banner = '''

UUID: {}
IPv6: {}
IPv4: {}
End of Life: {}

May take a few more moments to come online.

'''.format(node_uuid,
           node.ip6,
           node.ip4,
           node.end_of_life)

print(banner)

```


# Examples

* [Launch a tor relay](examples/torrelay.py)

# Licence

[Unlicense/Public domain](LICENSE.txt)
