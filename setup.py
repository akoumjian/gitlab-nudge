from setuptools import setup

setup(
    name='nudge',
    version='0.1',
    py_modules=['nudge'],
    install_requires=[
        'click==6.7',
        'requests==2.19.1',
        'pendulum==2.0.2'
    ],
    entry_points='''
        [console_scripts]
        nudge=nudge:run
    ''',
)
