from setuptools import setup, find_packages, Command

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'tests/runtests.py'])
        raise SystemExit(errno)

setup(
    name='epicslide',
    version='0.1',
    description='A landslide fork, lightweight markup language-based html5 slideshow generator',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    author='Anthony VEREZ',
    author_email='netantho@minet.net',
    url='http://epicslide.minet.net',
    license='Apache 2.0',
    platforms=['any'],
    keywords=[
        'markdown',
        'slideshow',
        'presentation',
        'rst',
        'restructuredtext',
        'textile'
    ],
    install_requires=[
        'Jinja2',
        'Markdown',
        'Pygments',
        'docutils',
        'WeasyPrint'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Text Processing :: Markup'
    ],
    long_description="""\
Epicslide takes your Markdown, RST, or Textile file(s) and generates a
slideshow.
""",
    entry_points={
        "console_scripts": [
            "epicslide = epicslide.main:main",
        ]
    },
      cmdclass = {'test': PyTest},
)


