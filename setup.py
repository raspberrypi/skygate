from setuptools import setup

setup(
    name='skygate',
    version='1.0',
    packages=['skygate'],
    url='www.daveakerman.com',
    license='GPL 2.0',
    author='Dave Akerman',
    author_email='dave@sccs.co.uk',
    description='HAB Receiver for RTTY and LoRa',
    scripts=[
        'skygate/skygate',
        'skygate/skygate_rtty',
        'skygate/toggle_skygate'
    ],
    install_requires=[
        'pygobject',
        'gpiozero',
        'setuptools',
        'pyserial',
        'spidev',
    ],
    include_package_data=True,
)

