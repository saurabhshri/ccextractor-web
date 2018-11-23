"""
ccextractor-web | instance/config.py

This is a secret config file, meaning the config variables in this file contain sensitive information and should not
reach git or be exposed. Each config variable is accompanied by the description and sample values are already filled in.
Make sure to replace them with your own values before deploying the application.

A more general configuration is present in the application root directory.
"""


"""
    Name:       SECRET_KEY
    Summary:    Enter the secret key, which is needed to keep the client-side sessions secure.
    Required:   Yes
    Tip:        Use the following command to quickly generate a random key

                $ python -c 'import os; print(os.urandom(16))'
                b'_5#y2L"F4Q8z\n\xec]/'
"""
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'


"""
    Name:       SQLALCHEMY_DATABASE_URI
    Summary:    Enter the URI to the database which will be used to create tables and store data.
    Required:   Yes
    URI:        'mysql+pymysql://username:password@server/db'

                E.g. If username = root, password = root, mysql server address = 127.0.0.1, database name = test,

                    then, URI = 'mysql+pymysql://root:root@127.0.0.1/test'.
"""
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1/test'


"""
    Name:       SECRET_CONFIG_READING_TEST
    Summary:    This value is used in one of the tests, leave it as it is.
    Required:   Yes
"""
SECRET_CONFIG_READING_TEST = 'It\'s a magical place.'


"""
    Name:       MAILGUN_PVT_API_KEY
                EMAIL_DOMAIN
    Summary:    Enter the mailgun API key and the registered domain. Used for sending emails.
    Required:   Yes
    Tip:        Here are the articles to help you find the API key and add domain
            
                https://help.mailgun.com/hc/en-us/articles/203380100-Where-can-I-find-my-API-key-and-SMTP-credentials-
                https://help.mailgun.com/hc/en-us/articles/203637190-How-do-I-add-a-domain-
"""
MAILGUN_PVT_API_KEY = 'key-xxxxxxxxxxxxxxxxxxxx'
EMAIL_DOMAIN = 'xxxxx.mailgun.org'

"""
    Name:       HMAC_KEY
    Summary:    Enter the shared key to be used for generating sha256 hashes.
    Required:   Yes
"""
HMAC_KEY = 'I have the high ground Anakin'


"""
    Name:       TEMP_UPLOAD_FOLDER
    Summary:    Enter the path to the directory where the uploaded files are temporarily saved before they are processed
                validated and moved to video repository.
    Required:   Yes
    Tip:        If full path is not provided, it'll use the path relative to the application root directory.
"""
TEMP_UPLOAD_FOLDER = 'files/temp/'


"""
    Name:       VIDEO_REPOSITORY
    Summary:    Enter the path to the directory where the video files should be stored. The uploaded files, upon 
                validation are kept in this directory. Files are copied to JOB directory from here.
    Required:   Yes
    Tip:        If full path is not provided, it'll use the path relative to the application root directory.
"""
VIDEO_REPOSITORY = 'files/repository/'


"""
    Name:       LOGS_DIR
    Summary:    Enter the path to the directory where the daemon uploads the job log files. When 'viewing' or 
                'downloading' the log files, they are served from this directory.
    Required:   Yes
    Tip:        If full path is not provided, it'll use the path relative to the application root directory.
"""
LOGS_DIR = 'files/logs/'


"""
    Name:       OUTPUT_DIR
    Summary:    Enter the path to the directory where the daemon uploads the job output files. When 'viewing' or 
                'downloading' the output files, they are served from this directory.
    Required:   Yes
    Tip:        If full path is not provided, it'll use the path relative to the application root directory.
"""
OUTPUT_DIR = 'files/output/'


"""
    Name:       ENABLE_KVM
    Summary:    Determines if the application has KVM support or not. For more details about this, please refer to the
                README file.
    Required:   Yes
    Tip:        Set it to either True or False
"""
ENABLE_KVM = True


"""
    Name:       KVM_LINUX_NAME
                LINUX_JOBS_DIR
    Summary:    Enter the name of linux KVM (this name will be used to perform operation on the VM) and path to the 
                nfs mount shared with Linux KVM.
    Required:   Only if ENABLE_KVM = True and Linux platform is to be made available.
    Tip:        If full path is not provided, it'll use the path relative to the application root directory. 
"""
KVM_LINUX_NAME = 'ubuntu'
LINUX_JOBS_DIR = 'files/mount/jobs/'


"""
    Name:       KVM_WINDOWS_NAME
                WINDOWS_JOBS_DIR
    Summary:    Enter the name of windows KVM (this name will be used to perform operation on the VM) and path to the 
                nfs mount shared with Windows KVM.
    Required:   Only if ENABLE_KVM = True and Windows platform is to be made available.
    Tip:        If full path is not provided, it'll use the path relative to the application root directory. 
"""
KVM_WINDOWS_NAME = ''
WINDOWS_JOBS_DIR = ''


"""
    Name:       KVM_MAC_NAME
                MAC_JOBS_DIR
    Summary:    Enter the name of macOS KVM (this name will be used to perform operation on the VM) and path to the 
                nfs mount shared with macOS KVM.
    Required:   Only if ENABLE_KVM = True and macOS platform is to be made available.
    Tip:        If full path is not provided, it'll use the path relative to the application root directory. 
"""
KVM_MAC_NAME = ''
MAC_JOBS_DIR = ''


"""
    Name:       ENABLE_LOCAL_MODE
    Summary:    Determines if the application is to be set-up in 'local' mode or 'public' mode. For more details about 
                this, please refer to the README file.
    Required:   Yes
    Tip:        Set it to either True or False
"""
ENABLE_LOCAL_MODE = False


"""
    Name:       ADMIN_NAME
                ADMIN_EMAIL
                ADMIN_PWD
    Summary:    Creates an admin User, with these credentials. All the operations (upload, processing,
                deletion etc. are done through this account. For more details about this, please refer to 
                the README file.
    Required:   Yes
    Tip:        Set it to either True or False
"""
ADMIN_NAME = 'Administrator'
ADMIN_EMAIL = 'admin@ccextractor.web'
ADMIN_PWD = 'admin@ccextractor.web'
