#!/bin/sh

progress() {
	echo "$NAME: $*" > /dev/console
	echo "$NAME: $*"
}

# This runs at the top of cloud-init. We don't even have SSHD running without
# this.

export ASSUME_ALWAYS_YES=yes

export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin

# pkg isn't installed by default on vultr, but this will bootstrap it
# with the above option of ASSUME_ALWAYS_YES=yes

progress 'Starting pkg upgrade'
pkg upgrade

progress 'Starting pkg install'
pkg upgrade
pkg install openvpn

sysctl net.inet.ip.random_id=1
echo 'net.inet.ip.random_id=1' >> /etc/sysctl.conf

# May need to consider bandwidth allowances with the plan and how high the
# rate limit is. This is 2.6TiB theoretical max, but probably would be a little
# higher in one month.

# IPv6 global address has to be specified manually.
# We also may not have it unless we probe for it explictly.

echo 'ifconfig_vtnet0_ipv6="inet6 accept_rtadv"
rtsold_enable=YES
ipv6_activate_all_interfaces=YES
dumpdev="NO"
moused_enable="NO"
sendmail_enable="NONE"
ip6addrctl_policy="ipv6_prefer"' >> /etc/rc.conf

# This is rather ugly, I'm sorry.
ifconfig vtnet0 inet6 auto_linklocal
ifconfig vtnet0 inet6 accept_rtadv
ifconfig vtnet0 inet6 -ifdisabled

service rtsold start
rtsold -fd1 vtnet0
sleep 10
rtsold -fd1 vtnet0
IPV6="$(ifconfig vtnet0 | grep inet6 | grep -v 'inet6 fe80' | awk '{print $2}')"

mkdir /usr/local/etc/openvpn

cd /usr/local/etc/openvpn

openvpn --genkey --secret static.key

echo 'dev tun
cipher AES-256-CBC
ifconfig 192.168.197.1 192.168.197.2
secret static.key
comp-lzo
keepalive 10 60
ping-timer-rem
tun-mtu 1280
persist-tun
persist-key' > openvpn.conf

echo 'firewall_enable="YES"
firewall_type="open"

gateway_enable="YES"
natd_enable="YES"
natd_interface="vtnet0"
natd_flags="-dynamic -m"' >> /etc/rc.conf

ifconfig vtnet0 -rxcsum -txcsum -vlanmtu -tso4 -tso6 -lro -vlanhwcsum -rxcsum6 -txcsum6 -vlanhwtso

client:

remote IP 1194
dev tun
ifconfig 192.168.197.2 192.168.197.1
comp-lzo
keepalive 10 60
ping-timer-rem
persist-tun
persist-key
redirect-gateway autolocal
dhcp-option DNS 8.8.8.8
fragment 1280
mssfix 1280
tun-mtu 1280

<secret>
-----BEGIN OpenVPN Static key V1-----
-----END OpenVPN Static key V1-----
</secret>

