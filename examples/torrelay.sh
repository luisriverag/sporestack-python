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
pkg install tor

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
if [ -n "$IPV6" ]; then
	echo "ORPort [$IPV6]:443" > /usr/local/etc/tor/torrc
fi
echo 'ORPort 443
Nickname BuiltAutomatically
RelayBandwidthRate 1024 KB
RelayBandwidthBurst 1024 KB
ContactInfo IThinkIWasBuiltAutomatically
ExitPolicy reject *:*
ExitPolicy reject6 *:*' >> /usr/local/etc/tor/torrc


# Running tor as root, partly for port 443 use. Since this server hopefully
# only runs tor, it's safe to do.
echo 'ntpd_enable="YES"
tor_enable="YES"
tor_user="root"' >> /etc/rc.conf

chown 0:0 /var/db/tor

service ntpd start
service tor start
