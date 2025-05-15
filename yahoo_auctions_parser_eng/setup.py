from setuptools import setup, find_packages

# pip install -e . Install package
# yaparser - parser
# yaprocess - process

setup(
    name="yahoo_auctions_parser",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4>=4.12.0',
        'python-dotenv>=1.0.0',
        'requests>=2.31.0',
        'gspread>=5.11.2',
        'oauth2client>=4.1.3',
        'googletrans>=4.0.0-rc1'
    ],
    entry_points={
        'console_scripts': [
            'yaparser=parse_auctions:main',
            'yaprocess=process_csv:main'
        ]
    }
)
