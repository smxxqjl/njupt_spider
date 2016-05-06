# -*- coding=UTF-8
from pymongo import MongoClient
#from gridfs import GridFS

class MongoDB_Driver:
    '''
    :db_ip mongodb　服务器地址　默认为localhost
    :db_port 端口号　默认为40029
    :db_databasename 数据库名称，
    '''
    def __init__(self,db_ip='127.0.0.1',db_port=40029,database_name='test'):
        self.db_conn=self.db_connect(db_ip,db_port)
        self.database=self.db_conn[database_name]
        self.col=None
    '''
    @:return 返回数据库链接，失败则返回None
    '''
    def db_connect(self,db_ip,db_port):

        try:
            mongo=MongoClient(db_ip,db_port)
        except:
            return None
        else:
            return mongo
    '''
    @param codition 条件，Dictionary 对象 ,such as {'name':smartlxh,'age':21}
     ＠:param collection 集合
     @:return 游标
    '''
    def db_findOne(self,collection,condition):
        self.col=self.database[collection]
        cursor=self.col.find_one(condition)
        return cursor
    '''
    同db_findone
    '''
    def db_findAll(self,collection,codition):
        self.col=self.database[collection]
        cursor=self.col.find(codition)
        return cursor
    '''
     @:param dictionary 插入的对象
     ＠:param collection 指定要插入的集合
     ＠:return success ---true,fail--false
    '''
    def db_insert(self,collection,dictionary):
        self.col=self.database[collection]
        try:
            self.col.insert(dictionary)
        except :
            print("error")
            return False
        else:
            return  True
    def db_remove(self,collection,dictionary):
        self.col=self.db_conn[collection]
        try:
            self.col.remove()
        except:
            return False
        else:
            return True
    def db_getCollectionNames(self, collection):
        collections = self.database.collection_names()
        return collections
        pass
    def fs_upload(self,path,filename,dbname):
        db=self.db_conn[dbname]
        fs=GridFS(db)
        fs.put(filename,path)
    '''
      @:function 在gridfs 中下载文件
      @:param dbname 数据库名字
      ＠:param file 要下载的文件名字
    '''
    def fs_download(self,filename,dbname,path):
        db=self.db_conn[dbname]
        fs=GridFS[db]
        file=fs.get_last_version(filename=filename)
        print(file.read())
    '''
      @:function 在gridfs 中删除文件
      @:param dbname 数据库名字
      ＠:param file 要删除的文件名字
    '''

    def fs_remove(self,dbname,file):
        db=self.db_conn[dbname]
        fs=GridFS(db)

        file=fs.get_last_version(filename=file)
        fs.delete(file._id)
mon=MongoDB_Driver()
mon.db_insert('Data',{'destination':'nanjing'})
