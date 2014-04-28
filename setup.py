from setuptools import setup, find_packages

def get_depends():
    """
    Get dependencies from requirements.txt file.
    requirements.txt contains pip output. This is handy to determine pyatta dependencies.
    e.g : pip freeze > requirements.txt
    """
    with open('requirements.txt','r') as f:
        return f.read().splitlines()

setup(
    name='pyatta',
    version='0.1.dev-r5581b',
    description='REST API for vyatta/vyos router OS.',
    long_description='A python REST API to configure and manage vyatta/vyos router.',
    url='http://github.com/vaytess/pyatta',
    author='Mootez Bessifi, Mohamed Abidi, Ahmed Bessifi',
    author_email='ahmed.bessifi@gmail.com',
    license='GPLv3',
    packages=find_packages(exclude='tests'),
    install_requires=get_depends(),
    zip_safe=False,
    platforms=['Linux'],
    data_files=[
        ('/etc/pyatta',['pyatta.conf'])
    ],
)
