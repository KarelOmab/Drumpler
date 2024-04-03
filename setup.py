from setuptools import setup, find_packages

setup(
    name='drumpler',
    version='1.0.0',
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
        'requests',
        'schedule',
        'psycopg2-binary',
    ],
)
