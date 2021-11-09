from setuptools import setup

setup(
    name='blubber_tools',
    version='0.1.0',
    py_modules=['blubber_tools'],
    install_requires=[
        'Click',
        'blubber-orm'
    ],
    entry_points={
        'console_scripts': [
            'blubber = blubber_tools.run:cli',
        ],
    },
)
