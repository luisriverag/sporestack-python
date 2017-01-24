Python library for http://sporestack.com/

# Installation

* `pip install sporestack`

# In action

[![asciicast](https://asciinema.org/a/98672.png)](https://asciinema.org/a/98672)

# Usage

View available options (osid, dcid, flavor) as a dict.

```
def node_options():
    """
    Returns a dict of options for osid, dcid, and flavor.
    """
```


Spawn a node.

```
def node(days,
         unique,
         sshkey=None,
         cloudinit=None,
         startupscript=None,
         osid=None,
         dcid=None,
         flavor=None):
    """
    Returns a node

    Returns:
    node.payment_status
    node.end_of_life
    node.ip6
    node.ip4
    """
```

Or use the helper application:

```
$ sporestack spawn
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

# sporestack spawn QR behavior

Requires a fairly wide terminal for the QR code. Also, flashes up with alternating QR code colors to work with reversed and normal terminals.

# Deprecation notice

`nodemeup` has been replaced by `sporestack spawn`.

# Licence

[Unlicense/Public domain](LICENSE.txt)
