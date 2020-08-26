# Python 3 library and CLI for [SporeStack](https://sporestack.com) [.onion](http://spore64i5sofqlfz5gq2ju4msgzojjwifls7rok2cti624zyq3fcelad.onion)

## Installation

* `pip3 install sporestack || pip install sporestack`

## Screenshot

![sporestackv2 CLI screenshot](https://sporestack.com/static/sporestackv2-screenshot.png)

## Usage

* `sporestackv2 launch SomeHostname --flavor vps-1vcpu-1gb --days 7 --ssh_key_file ~/.ssh/id_rsa.pub --operating_system debian-9 --currency btc`
* `sporestackv2 topup SomeHostname --days 3 --currency bsv`
* `sporestackv2 launch SomeOtherHostname --flavor vps-1vcpu-2gb --days 7 --ssh_key_file ~/.ssh/id_rsa.pub --operating_system debian-10 --currency btc`
* `sporestackv2 stop SomeHostname`
* `sporestackv2 start SomeHostname`
* `sporestackv2 list`
* `sporestackv2 remove SomeHostname # If expired`
* `sporestackv2 settlement_token_generate`
* `sporestackv2 settlement_token_enable (token) --dollars 10 --currency xmr`
* `sporestackv2 settlement_token_add (token) --dollars 25 --currency btc`
* `sporestackv2 settlement_token_balance (token)`

More examples on the [website](https://sporestack.com).

## Notes

 * You can use --walkingliberty_wallet if you don't want to pay by QR codes all the time, or you can use --settlement_token. --settlement_token is probably better for most.
 * As of 1.0.7, will try to use a local Tor proxy if connecting to a .onion URL. (127.0.0.1:9050) (However, this does not apply to `serialconsole` for the time being.)

## Tips

If using Hidden Hosting, configure ~/.ssh/config like this (fixes serialconsole and you can ssh without torsocks):

```
Host *.onion
        ProxyCommand nc -x localhost:9050 %h %p
```

## Deprecation notice

Use `sporestackv2` instead of `sporestack`.

## Licence

[Unlicense/Public domain](LICENSE.txt)
