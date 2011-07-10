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
        'django-storages>=1.2a',
        'boto'
    ],
    dependency_links = [
        'https://bitbucket.org/david/django-storages/get/tip.zip#egg=django-storages-1.2a'
    ]
)