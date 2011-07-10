Python developer test task
==========

Requirements
----------

#) Code style by http://www.python.org/dev/peps/pep-0008/
#) Project deployment using http://pypi.python.org/pypi/zc.buildout and providing installation instructions in INSTALL.txt in code root folder
#) Should be published on https://github.com/
#) Commented code is a plus

The task
----------

Build a web application using latest django/pyramid/gae, which will allow:
- log in using twitter or google auth
- upload a file, which should be stored on amazon s3 service (there should be special settings in config for that)
- view list of your uploaded files
- ability to view and share the file with any other people by sending link to them (have an action and form asking email(s) and optional message to the person). Going by link people should be able to download or view file in google docs using google docs api, of course if file type allows to be viewed though it

Strict requirement: application should not reload browser page at all, so all should be done using ajax technology.
Recommendations: reuse as much existing django apps/tool as possible and you will win :)
Always remember the KISS principle

Notes
=========

3rd party applications
---------

- jQuery - JS framework http://jquery.com/
- jQuery.form - AJAX form submission http://jquery.malsup.com/form/
- jQuery.address - AJAX deep linking http://www.asual.com/jquery/address/
- Pure - JS template engine http://beebole.com/pure/
- Blueprint - CSS framework http://www.blueprintcss.org/
- django - The Web framework for perfectionists with deadlines http://www.djangoproject.com/
- django-storages - support for Amazon S3 filestorage http://bitbucket.org/david/django-storages/wiki/Home
- south - Django DB migration tools http://south.aeracode.org/
- django-social-auth - Login with Google or Twitter account http://pypi.python.org/pypi/django-social-auth/

TODO
--------

- Test coverage
- Make views work without csrf_exempt
- Make Pure blocks more flexible