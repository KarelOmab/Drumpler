from setuptools import setup, find_packages
# Function to read the version from __version__.py
def get_version(rel_path):
    with open(rel_path, 'r') as file:
        for line in file:
            if line.startswith('__version__'):
                delimiters = '"\''
                quote = line.split('=')[1].strip()[0]
                return line.split(quote)[1]
    raise RuntimeError("Unable to find version string.")

setup(
    name='Drumpler',
    version=get_version("drumpler/__version__.py"),
    author='Karel Tutsu',
    author_email='karel.tutsu@gmail.com',
    description='Framework for rapidly developing a restful API that requires post processing',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/KarelOmab/Drumpler',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'Flask',
        'python-dotenv',
        'SQLAlchemy',
        'Flask_SQLAlchemy',
        'psycopg2-binary',
        'psutil'
    ],
)
