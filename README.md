Google Cloud Bucket Manager
==============================

Python package with tools to manage a Google Cloud Bucket instance.


Installation:
---------
```
pip install git+https://github.com/simonsanvil/googleBucketManager
```

Features:
---------

Besides allowing you to manage the files in your bucket you can also download all files in an specific folder of your bucket to a local directory and sync them.

Check the following Google Colab for examples about how to integrate this package with your Google Colab project:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/simonsanvil/googleBucketManager/blob/master/notebooks/1-colab_notebook_showcase.ipynb)

---------------

Usage
---------

Before a BucketManager class instance is created you need to have set `GOOGLE_APPLICATION_CREDENTIALS` in your environmental variables. See the Google docs [Getting started with authentication](https://cloud.google.com/docs/authentication/getting-started) to see how this is obtained. 


```python
from googleBucketManager import GoogleBucketManager

bucket_manager = GoogleBucketManager(bucket_name='my-bucket')
```

List all blobs (files) in a bucket:

```python
bucket_manager.list_bucket()
```
List blobs in an specific folder of your bucket:
```python
bucket_manager.list_dir('path/to/bucket/folder')
```
Delete a blob from your bucket:
```python
bucket_manager.delete_blob('bucket/path/to/blob')
```
Upload local file to your remote bucket:
```python
bucket_manager.upload_blob('local/path/to/file','bucket/path/to/new/blob')
```
Download file from your remote bucket to a local path:
```python
bucket_manager.download_blob('bucket/path/to/blob','local/path/to/new/file')
```
Download a folder from your remote bucket to a local directory:
```python
bucket_manager.download_folder('bucket/path/to/folder','local/path/to/new/folder')
```
Connect a local directory with a remote bucket folder and sync them:
```python
bucket_manager.link_sync('bucket/path/to/folder-to-sync','local/path/to/directory-to-sync')

#...
## After making changes to the specified local directory
# and you are ready to sync the remote bucket run the following 
# command to apply your local changes to the respective bucket folder
manager.sync_bucket() 
```

--------
