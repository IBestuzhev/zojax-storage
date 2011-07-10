from distutils.core import setup

setup(
    name='django-ibstorage',
    version='1.00',
    description="Test task for Zojax Group",
    author="Igor Bestuzhev",
    author_email="best.igor@gmail.com",
    packages=['ibstorage'],
    package_dir={"":'src'},
    install_requires=[
        'setuptools',
        'django==1.3',
        'south',
        'django-social-auth',
    ],
    dependency_links = []
)