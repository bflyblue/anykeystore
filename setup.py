from distutils.core import setup

setup(
    name='anykeystore',
    version='0.1.0',
    author='Shaun Sharples',
    author_email='shaun.sharples@gmail.com',
    packages=['anykeystore'],
    url='https://github.com/bflyblue/anykeystore',
    license='LICENSE.txt',
    description='Wrap backends as simple key-value stores.',
    long_description=open('README.rst').read(),
)
