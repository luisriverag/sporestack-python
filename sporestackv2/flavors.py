from typing import NamedTuple


class Flavor(NamedTuple):
    # Unique string to identify the flavor that's sort of human readable.
    slug: str
    # Number of vCPU cores the server is given.
    cores: int
    # Memory in Megabytes
    memory: int
    # Disk in Gigabytes
    disk: int
    # USD cents per day
    price: int
    # IPv4 connectivity: "/32" or "tor". If "tor", needs to match IPv6 setting.
    ipv4: str
    # IPv6 connectivity: "/128" (may act as a /64, may not) or tor. If "tor", needs to match IPv4 setting.
    ipv6: str
    # Gigabytes of bandwidth per day
    bandwidth: int


# This one is too small to work reliably with iPXE.
#    "tor-512": Flavor(
#        slug="tor-512",
#        cores=1,
#        memory=512,
#        disk=4,
#        price=14,
#        ipv4="tor",
#        ipv6="tor",
#        bandwidth=10,
#    ),
all_sporestack_flavors = {
    "tor-1024": Flavor(
        slug="tor-1024",
        cores=1,
        memory=1024,
        disk=8,
        price=28,
        ipv4="tor",
        ipv6="tor",
        bandwidth=20,
    ),
    "tor-2048": Flavor(
        slug="tor-2048",
        cores=1,
        memory=2048,
        disk=16,
        price=56,
        ipv4="tor",
        ipv6="tor",
        bandwidth=40,
    ),
    "tor-3072": Flavor(
        slug="tor-3072",
        cores=1,
        memory=3072,
        disk=24,
        price=84,
        ipv4="tor",
        ipv6="tor",
        bandwidth=60,
    ),
    "tor-4096": Flavor(
        slug="tor-4096",
        cores=1,
        memory=4096,
        disk=32,
        price=112,
        ipv4="tor",
        ipv6="tor",
        bandwidth=80,
    ),
}
