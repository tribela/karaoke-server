import os.path

try:
    from setuptools import find_packages, setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import find_packages, setup


def readfile(filename):
    try:
        with open(os.path.join(os.path.dirname(__file__), filename)) as f:
            return f.read()
    except (IOError, OSError):
        return ''


install_reqs = [
    'Flask>=0.10.1',
    'SQLAlchemy>=0.9.7',
    'lxml>=3.3.5',
    'python-dateutil>=2.2',
    'requests>=2.8.1',
    'six>=1.7.3',
]


setup(
    name='karaokeserver',
    description='Database update server for KaraokeBook',
    long_description=readfile('README.md'),
    url='http://kjwon15.net/',
    download_url='https://github.com/Kjwon15/karaoke-server/releases',
    author='Kjwon15',
    author_email='kjwonmail@gmail.com',
    entry_points={
        'console_scripts': [
            'karaoke-server = karaokeserver.command:main'
        ]
    },
    packages=find_packages(),
    install_requires=install_reqs,
)
