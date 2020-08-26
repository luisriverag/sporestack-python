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
    "vps-1vcpu-1gb": Flavor(
        slug="vps-1vcpu-1gb",
        cores=1,
        memory=1024,
        disk=25,
        price=32,
        ipv4="/32",
        ipv6="/128",
        bandwidth=36,
    ),
    "vps-1vcpu-2gb": Flavor(
        slug="vps-1vcpu-2gb",
        cores=1,
        memory=2048,
        disk=50,
        price=64,
        ipv4="/32",
        ipv6="/128",
        bandwidth=73,
    ),
    "vps-3vcpu-1gb": Flavor(
        slug="vps-3vcpu-1gb",
        cores=3,
        memory=1024,
        disk=60,
        price=96,
        ipv4="/32",
        ipv6="/128",
        bandwidth=109,
    ),
    "vps-2vcpu-2gb": Flavor(
        slug="vps-2vcpu-2gb",
        cores=2,
        memory=2048,
        disk=60,
        price=96,
        ipv4="/32",
        ipv6="/128",
        bandwidth=109,
    ),
    "vps-1vcpu-3gb": Flavor(
        slug="vps-1vcpu-3gb",
        cores=1,
        memory=3072,
        disk=60,
        price=96,
        ipv4="/32",
        ipv6="/128",
        bandwidth=109,
    ),
    "vps-2vcpu-4gb": Flavor(
        slug="vps-2vcpu-4gb",
        cores=2,
        memory=4096,
        disk=80,
        price=128,
        ipv4="/32",
        ipv6="/128",
        bandwidth=146,
    ),
    "vps-4vcpu-8gb": Flavor(
        slug="vps-4vcpu-8gb",
        cores=4,
        memory=8192,
        disk=160,
        price=257,
        ipv4="/32",
        ipv6="/128",
        bandwidth=182,
    ),
    "vps-6vcpu-16gb": Flavor(
        slug="vps-6vcpu-16gb",
        cores=6,
        memory=16384,
        disk=320,
        price=514,
        ipv4="/32",
        ipv6="/128",
        bandwidth=219,
    ),
    "vps-8vcpu-32gb": Flavor(
        slug="vps-8vcpu-32gb",
        cores=8,
        memory=32768,
        disk=640,
        price=1028,
        ipv4="/32",
        ipv6="/128",
        bandwidth=256,
    ),
    "vps-12vcpu-48gb": Flavor(
        slug="vps-12vcpu-48gb",
        cores=12,
        memory=49152,
        disk=960,
        price=1542,
        ipv4="/32",
        ipv6="/128",
        bandwidth=292,
    ),
    "vps-16vcpu-64gb": Flavor(
        slug="vps-16vcpu-64gb",
        cores=16,
        memory=65536,
        disk=1280,
        price=2057,
        ipv4="/32",
        ipv6="/128",
        bandwidth=329,
    ),
    "vps-20vcpu-96gb": Flavor(
        slug="vps-20vcpu-96gb",
        cores=20,
        memory=98304,
        disk=1920,
        price=3085,
        ipv4="/32",
        ipv6="/128",
        bandwidth=365,
    ),
    "vps-24vcpu-128gb": Flavor(
        slug="vps-24vcpu-128gb",
        cores=24,
        memory=131072,
        disk=2560,
        price=4114,
        ipv4="/32",
        ipv6="/128",
        bandwidth=402,
    ),
    "vps-32vcpu-192gb": Flavor(
        slug="vps-32vcpu-192gb",
        cores=32,
        memory=196608,
        disk=3840,
        price=6171,
        ipv4="/32",
        ipv6="/128",
        bandwidth=438,
    ),
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
