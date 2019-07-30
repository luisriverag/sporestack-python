# Python 3 library and CLI for [SporeStack](https://sporestack.com) [.onion](http://spore64i5sofqlfz5gq2ju4msgzojjwifls7rok2cti624zyq3fcelad.onion)

## Installation

* `pip3 install sporestack || pip install sporestack`

## Screenshot

![sporestackv2 CLI screenshot](https://sporestack.com/static/sporestackv2-screenshot.png)

## Usage

* `sporestackv2 launch SomeHostname --days 7 --ssh_key_file ~/.ssh/id_rsa.pub --operating_system debian-9 --currency btc`
* `sporestackv2 topup SomeHostname --days 3 --currency bsv`
* `sporestackv2 stop SomeHostname`
* `sporestackv2 start SomeHostname`
* `sporestackv2 list`
* `sporestackv2 remove SomeHostname # If expired`

More examples on the [website](https://sporestack.com).

# Notes

You can use --walkingliberty_wallet if you don't want to pay by QR codes all the time.

# Deprecation notice

Use `sporestackv2` instead of `sporestack`.

# Licence

[Unlicense/Public domain](LICENSE.txt)
