Google Cloud Bucket Manager
==============================

Python package with interfaces to manage a Google Cloud Bucket instance.

Installation:
---------
```
pip install git+git://github.com/simonsanvil/googleBucketManager.git
```

Features:
---------

Besides allowing you to manage the files in your bucket you can also download all files in an specific folder of your bucket to a local directory and sync them.

Usage
---------

Before a BucketManager class instance is created you need to have set `GOOGLE_APPLICATION_CREDENTIALS` in your environmental variables. See the google docs [Getting started with authentication](https://cloud.google.com/docs/authentication/getting-started) to see how this is obtained. 

```python
from googleBucketManager import GoogleBucketManager

bucket_manager = GoogleBucketManager(bucket_name='my-bucket')
```

List all blobs (files) in a bucket:

```python
bucket_manager.list_bucket()
```
List blobs in an specific folder of the bucket:
```python
bucket_manager.list_dir('path/to/bucket/folder')
```
Delete bucket blob:
```python
bucket_manager.delete_blob('bucket/path/to/blob')
```
Upload local file to bucket:
```python
bucket_manager.upload_blob('local/path/to/file','bucket/path/to/new/blob')
```
Download file from bucket to local path:
```python
bucket_manager.download_blob('bucket/path/to/blob','local/path/to/new/file')
```
Download remote bucket folder to a local directory:
```python
bucket_manager.download_folder('bucket/path/to/folder','local/path/to/new/folder')
```
Connect a local directory to a bucket folder and sync them:
```python
bucket_manager.link_sync('bucket/path/to/folder-to-sync','local/path/to/directory-to-sync')

#...
## After making changes to the specified local directory
# and you are ready to sync the remote bucket run the following 
# command to apply your local changes to the respective bucket folder
manager.sync_bucket() 
```



Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    │
    ├── docs              
    │    
    ├── notebooks          <- Jupyter notebooks.
    │
    ├── references         <- Manuals, and all other explanatory materials.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so googleBucketManager can be imported
    |
    └── googleBucketManager           <- Source code for use in this project. Can be installed as a python module

--------
