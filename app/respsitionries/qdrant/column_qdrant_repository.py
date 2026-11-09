from qdrant_client import AsyncQdrantClient


from app.conf.app_config import app_config

from qdrant_client.http import models

from app.core.log import logger
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


class ColumnQdrantRepository:
    #定义字段存储向量的集合名称
    collection_name = "data-agent-column"

    def __init__(self, qdrant_client:AsyncQdrantClient):
        self.qdrant_client = qdrant_client

    async def ensure_collection(self):
        '''
        确保存储字段向量的集合存在
        :return:
        '''
        #查询并判断执行集合是否存在
        if not await self.qdrant_client.collection_exists(collection_name=self.collection_name):
            #创建集合
            await self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=app_config.qdrant.embedding_size, distance=models.Distance.COSINE)
            )

    async def upsert_column_embeddings(self, ids:list[str], embeddings:list[list[float]], payloads:list[ColumnInfoQdrant], batch_size:int=10):
        '''
        保存向量字段道qdrant
        :param ids:
        :param embeddings:
        :param payloads:
        :return:
        '''
        #【（id，embbing，payload），（    id，embbing，payload    ），。。。】
        zipped = list(zip(ids, embeddings, payloads))
        for i in range(0, len(zipped), batch_size):
            #获取批量数据
            batch = zipped[i:i + batch_size]
            #转换结构为qdrant需要的结构 【PointStruct,PointStruct,PointStruct】
            points = [models.PointStruct(id=id, vector=embedding, payload=payload) for id, embedding, payload in batch]
            await self.qdrant_client.upsert(collection_name=self.collection_name, points=points)

            logger.info("为字段构建向量索引 {}".format(i))
