from setuptools import setup
import json
from os import path

here = path.abspath(path.dirname(__file__))
# root = path.dirname(here)

readme = path.join(here, 'README.md')
package_json = path.join(here, 'package.json')

# # a workaround when installing locally from git repository with pip install -e .
# if not path.isfile(package_json):
#     package_json = path.join(root, 'package.json')

# long description from README file
with open(readme, encoding='utf-8') as f:
    long_description = f.read()
    
# version number and all other params from package.json
with open(package_json, encoding='utf-8') as f:
    package = json.load(f)

setup(
    
    name="ccdxt",
    version="0.19",
    
    description=package['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    url=package['homepage'],
    author=package['author']['name'],
    author_email=package['author']['email'],
    license=package['license'],
    packages=["ccdxt"],
    # install_requires=['web3','eth-tester'],
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Environment :: Console'
    ],
    
    keywords=package['keywords'],
    
    install_requires=[
        "web3",
        "eth-tester==0.7.0b1"
    ],
    
    extras_require={
        
    }
    
)
