{
    'name': 'Unlink Attachment With Filestore',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': """When deleting attachment records, the corresponding filestore files are also removed.Unlinking attachments from the filestore in Odoo involves ensuring that when an attachment record is deleted from the database, the corresponding file stored in the filestore is also removed. This helps in maintaining a clean and efficient storage system, preventing orphaned files and saving disk space.
    Imagine you have a custom module where users upload and manage documents. You want to ensure that when a document is deleted from Odoo, the corresponding file in the filestore is also removed to prevent orphaned files and save storage space.
    Remove File Attachment from Filestore,Detach Attachment from Filestore,Delete Attachment from Storage,Unlink Document from Filestore,delete Document from Filestore
    Purge Attachment from Filestore,Delete Attachment from Storage
    Unlink File Attachment, Delete File Storage, File Store, Data Migration
""",
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/unlink_filestore.xml',
    ],
    'images': ['static/description/cover.png'],
    'author': 'Vraja Technologies',
    'website': 'https://www.vrajatechnologies.com',
    'live_test_url': 'https://www.vrajatechnologies.com/contactus',
    'installable': True,
    'application': True,
    'autoinstall': False,
    'license': 'OPL-1',
    'price': '49',
    'currency': 'EUR',
}
# Version Log
# 16.0.0 => Initial setup.
