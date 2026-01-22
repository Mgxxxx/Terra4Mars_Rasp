from setuptools import find_packages, setup

setup(
    name="rover_commands",
    version="1.0.0",
    packages=find_packages(exclude=["test"]),
    install_requires=[
        "setuptools",
        "pyserial",
        "pygame",
    ],
    zip_safe=True,
    maintainer="EPFL Xplore",
    maintainer_email="software@epfl-xplore.ch",
    description="PS4 controller interface for Terra4Mars rover",
    license="MIT",
    entry_points={
        "console_scripts": [
            "controller = rover_commands.controller:main",
            "sender = host.sender:main",
            "receiver = raspberry.receiver:main",
        ],
    },
)
