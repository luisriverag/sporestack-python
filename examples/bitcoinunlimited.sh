#!/bin/sh

# Stops/breaks at:
# In file included from leveldb/db/builder.cc:7:
# In file included from ./leveldb/db/filename.h:14:
# In file included from ./leveldb/port/port.h:14:
# ./leveldb/port/port_posix.h:38:12: fatal error: 'endian.h' file not found
#   #include <endian.h>
#            ^
# 1 warning and 1 error generated.
# gmake[2]: *** [Makefile:3874: leveldb/db/leveldb_libleveldb_a-builder.o] Error 1
#

progress() {
	echo "bitcoinunlimited: $*" > /dev/console
	echo "bitcoinunlimited: $*"
}

# This runs at the top of cloud-init. We don't even have SSHD running without
# this.

# <- Does it still do that?

export ASSUME_ALWAYS_YES=yes

export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin

progress 'Starting pkg upgrade'
pkg upgrade

progress 'Starting pkg install'
pkg upgrade
pkg install ca_root_nss autotools pkgconf gmake boost-libs libevent2 openssl db48 git micro_httpd micro_inetd #FIXME TODO: Remove git
chmod 700 /root
mkdir /root/.bitcoin
echo 'rpcuser=bitcoinunlimited
rpcpassword=bitcoinunlimitedpassword' > /root/.bitcoin/bitcoin.conf
# ^ If the user and password are the same, it will fail.

mkdir /root/BitcoinUnlimited

# tmpfs for speed and because / is too small otherwise.
# growfs seems to have problems, not sure why.
mount -t tmpfs tmpfs /root/BitcoinUnlimited
cd /root/BitcoinUnlimited
#FIXME This seems to have a 302 loop right now.
#fetch -qo - https://github.com/bitcoinunlimited/bitcoinunlimited/archive/$TAG.tar.gz | tar xzf -

progress 'Starting git clone'
git clone --depth 1 https://github.com/BitcoinUnlimited/BitcoinUnlimited.git bu-src
cd BitcoinUnlimited
./autogen.sh
./configure --with-gui=no --without-miniupnpc --disable-wallet
progress 'About to compile'
gmake -j 2
gmake install
cd /
umount /root/BitcoinUnlimited

fetch -q \
https://raw.githubusercontent.com/teran-mckinney/bitnoder/master/fs/etc/rc.local \
-o /etc/rc.local

fetch -q \
https://raw.githubusercontent.com/teran-mckinney/bitnoder/master/fs/usr/local/bin/honeybadgermoneystats \
-o /usr/local/bin/honeybadgermoneystats

echo > /usr/local/etc/bitnoder.conf

echo 'ntpd_enable="YES"' >> /etc/rc.conf

chmod 500 /etc/rc.local
chmod 500 /usr/local/bin/honeybadgermoneystats

# Let the boot process start rc.local on its own.
#/etc/rc.local
