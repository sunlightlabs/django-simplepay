from distutils.core import setup

long_description = open('README.rst').read()

setup(
    name='django-simplepay',
    version="0.2",
    packages=['simplepay'],
    package_dir={'simplepay': 'simplepay'},
    package_data={'simplepay': ['templates/simplepay/*.html']},
    description='Amazon Simple Pay buttons',
    author='Jeremy Carbaugh',
    author_email='jcarbaugh@sunlightfoundation.com',
    license='BSD License',
    url='http://github.com/sunlightlabs/django-simplepay/',
    long_description=long_description,
    platforms=["any"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
)