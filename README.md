Python library for http://sporestack.com/

# Installation

* `pip install sporestack`

# In action

[![asciicast](https://asciinema.org/a/98672.png)](https://asciinema.org/a/98672)

# Usage

Use the helper application:

```
$ sporestack spawn
```

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

# Examples

* `sporestack spawn --sporestackfile examples/torrelay.json`

# sporestack spawn QR behavior

Requires a fairly wide terminal for the QR code. Also, flashes up with alternating QR code colors to work with reversed and normal terminals.

# Deprecation notice

`nodemeup` has been replaced by `sporestack spawn`.

# Licence

[Unlicense/Public domain](LICENSE.txt)
