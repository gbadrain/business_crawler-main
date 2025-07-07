from setuptools import setup, find_packages

setup(
    name='business-crawler',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ddgs',
        'requests',
        'trafilatura',
        'pandas',
        'spacy',
        'pytest',
        'ruff',
        'black',
        'tqdm',
        'matplotlib',
        'seaborn',
    ],
    entry_points={
        'console_scripts': [
            'business-crawler=main:main',
        ],
    },
    author='Gurpreet Singh Badrain',
    author_email='gbadrain@gmail.com',
    description='A modular and extensible pipeline that automates web research at scale.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gbadrain/business-crawler', # Replace with your actual GitHub repo URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Text Processing :: General',
    ],
    python_requires='>=3.9',
)
