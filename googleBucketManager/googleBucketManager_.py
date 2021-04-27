import os
from google.cloud import storage 

class GoogleBucketManager():

  def __init__(self,google_app_creds=None,bucket_name=None,ignore=[]):
    if google_app_creds is None:
      assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'google_app_creds not given and GOOGLE_APPLICATION_CREDENTIALS is not set'
    else:
      os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_app_creds

    if bucket_name is None:
      assert 'BUCKET_NAME' in os.environ, 'bucket_name not given and BUCKET_NAME is not set'
      self.bucket_name = os.environ['BUCKET_NAME']
    else:
      self.bucket_name = bucket_name
    
    self.storage_client = storage.Client()
    self.bucket = self.storage_client.get_bucket(self.bucket_name) 

    self.toignore = ['.ipynb_checkpoints/'] + ignore 
    self.dirs_to_observe = []
    
  
  def link_sync(self,bucket_dir,local_dir):
    self.dirs_to_observe += [(bucket_dir,local_dir)]
  
  def download_folder(self,folder=None,destination_folder=None):
    if folder==None and destination_folder==None:
      destination_folder = self.bucket_name
    if folder==None:
      folder=''
    if destination_folder==None:
      destination_folder = folder

    if not os.path.isdir(destination_folder):
      os.mkdir(destination_folder)
    
    folder_blobs = self.list_dir(folder)
    for blob_name in folder_blobs:
      if os.path.split(blob_name)[0]==folder:
        destination_fname = os.path.join(destination_folder,'/'.join(os.path.split(blob_name)[1:]))
      else:
        destination_fname = os.path.join(destination_folder,blob_name)
      if blob_name.endswith("/"):
        if not os.path.isdir(destination_fname[:-1]):
          os.mkdir(destination_fname[:-1])
        continue
      self.download_blob(blob_name,destination_fname)
    
    print(f"All files in {self.bucket_name}/{folder}/.. have been downloaded to {destination_folder}/..")
    return destination_folder

  def sync_all(self):
    for remote_dir,local_dir in self.dirs_to_observe:
      #sync all
      pass
  
  def sync_local(self):
    for remote_dir,local_dir in self.dirs_to_observe:
      #sync local folders
      pass
    
  def ignore(self,toignore):
    if isinstance(toignore,str):
      toignore = [toignore]
    self.toignore += toignore

  def sync_bucket(self,verbose=True):
    for bucket_dir,local_dir in self.dirs_to_observe:
      #sync the bucket by uploading all local files to the bucket and deleting those that are in the bucket but not locally
      if bucket_dir is None or bucket_dir=='.':
        bucket_dir = ''
      for parentdir,subdirs,dirfiles in os.walk(local_dir):
        if parentdir in self.toignore or parentdir+'/'in self.toignore: continue
        if parentdir==local_dir:
          parentdir = parentdir+'/'
        equivalent_dir = bucket_dir+'/'+'/'.join(os.path.split(parentdir)[1:])
        #print(f'{equivalent_dir}/ is equivalent to {parentdir}/')
        dirblobs = [(b,os.path.split(b)[-1]) for b in self.list_dir(equivalent_dir)]
        #print(f'dirblobs: {dirblobs}, subdirs: {subdirs}')
        for blob,blobname in dirblobs: #remove from the bucket files and directories that were removed locally
          if blobname not in dirfiles and blobname not in [s+'/' for s in subdirs]:
            self.delete_blob(blob,verbose=verbose)
        for subdir in subdirs: #check for new local subdirectories and create them in the bucket
          if subdir in self.toignore or subdir+'/'in self.toignore: continue
          if subdir+'/' not in [b for _,b in dirblobs]:
            self.create_folder(os.path.join(equivalent_dir,subdir),verbose=verbose)
        for fname in dirfiles: #check for new local files and create them in the bucket
          if fname in self.toignore or fname+'/'in self.toignore: 
            continue
          local_fpath = os.path.join(parentdir,fname)
          bucket_blobpath = os.path.join(equivalent_dir,fname)
          self.upload_blob(local_fpath,bucket_blobpath,verbose=verbose)
    print("bucket synced succesfully!")
  
  def create_folder(self,folder_name,verbose=True):
    bucket = self.storage_client.get_bucket(self.bucket_name)
    dirblob = bucket.blob(folder_name+'/')
    dirblob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')
    if verbose:
      print(f"{folder_name}/ created")
  
  def delete_blob(self,blob_name,verbose=True):
    """Deletes a blob from the bucket."""
    bucket_name = self.bucket_name
    bucket = self.storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
    if verbose:
      print("Blob {} deleted.".format(blob_name))

  def get_blob(self,blob_name):
    '''returns a blob in the bucket from its name'''
    bucket_name = self.bucket_name
    bucket = self.storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob

  
  def upload_blob(self,source_file_name, destination_blob_name,verbose=True,deep_rewrite=True):
    """
    Uploads a file to the bucket.

    If deep_overwrite is set to True and the uploaded blob has the same path as an  alrady existing blob in the bucket
    then the permissions and metadata of the old blob will be copied to the new one. 
    """
    bucket_name = self.bucket_name
    bucket = self.storage_client.bucket(bucket_name)

    if destination_blob_name in self.list_dir("",fullpath=False) and deep_rewrite:
      # print(f"{destination_blob_name} exists. Will be rewrited")
      oldblob = self.get_blob(destination_blob_name)
      ispublic = "READER" in oldblob.acl.all().get_roles()
      metadata = oldblob.metadata
      blob = bucket.blob(destination_blob_name)
      blob.metadata = metadata
    else:  
      ispublic = False
    
    blob = bucket.blob(destination_blob_name)
    ispublic = "READER" in blob.acl.all().get_roles()
    meta = blob.metadata

    blob.upload_from_filename(source_file_name)
    blob = bucket.blob(destination_blob_name)
    if deep_rewrite:
      if ispublic:
        blob.make_public()
      blob.metadata = meta
    
    if verbose:
      print(
          "File {} uploaded to {} (public: {}).".format(
              source_file_name, destination_blob_name,ispublic
          )
      )

  def list_dir(self,folder,fullpath=True):
    """Lists all the blobs in a bucket folder."""

    if folder is None:
      folder = ""
      
    folder = folder+"/" if len(folder)>0 and not folder.endswith("/") else folder
    
    bucket_name = self.bucket_name

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = self.storage_client.list_blobs(bucket_name,prefix=folder)
    if fullpath:
      return [blob.name for blob in blobs][1:]
    else:
      return [blob.name[(len(folder)):] for blob in blobs][1:]

  def list_bucket(self):
    """Lists all the blobs in a bucket."""
    bucket_name = self.bucket_name

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = self.storage_client.list_blobs(bucket_name)

    return [blob.name for blob in blobs]
    

  def download_blob(self,source_blob_name, destination_file_name=None,verbose=True):
    """Downloads a blob from the bucket."""
    bucket_name = self.bucket_name
    destination_file_name = destination_file_name if destination_file_name is not None else source_blob_name

    bucket = self.storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    if verbose:
      print(
          "Blob {} downloaded to {}.".format(
              source_blob_name, destination_file_name
          )
      )