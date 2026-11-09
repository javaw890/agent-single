from numpy import random
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import models
import asyncio


from app.conf.app_config import app_config


class QdrantClientManager():
    '''
    Qdrant客户端
    '''
    def __init__(self,qdrant_config):
        self.qdrant_config = qdrant_config
        self.client:None|AsyncQdrantClient=None
        pass

    def _get_url(self):
        """
        拼接Qdrant服务的连接URL
        :return: 符合Qdrant客户端要求的http连接地址
        """
        return f"http://{self.qdrant_config.host}:{self.qdrant_config.port}"
    def init(self):
        self.client = AsyncQdrantClient(self._get_url())
    async def close(self):
        """异步关闭Qdrant客户端，释放连接资源"""
        await self.client.close()


# 实例化Qdrant客户端管理器（传入全局配置中的Qdrant配置）
qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == '__main__':
    # 初始化Qdrant异步客户端
    qdrant_client_manager.init()
    qdrant_client = qdrant_client_manager.client


    async def test():
        if not await qdrant_client.collection_exists(collection_name="my_collection"):
            await qdrant_client.create_collection(
                collection_name="my_collection",  # 集合名称（类似数据库表名）
                # 向量字段配置：10维向量，使用余弦相似度计算
                vectors_config=models.VectorParams(size=10, distance=models.Distance.COSINE),
            )
        await qdrant_client.upsert(
            collection_name="my_collection",
            # 列表推导式生成100个PointStruct对象（包含ID和随机向量）
            points=[
                models.PointStruct(
                    id=i,  # 向量唯一标识ID
                    vector=[random.random() for _ in range(10)]  # 生成10维随机向量
                )
                for i in range(100)
            ],
        )
        res = await qdrant_client.query_points(
            collection_name="my_collection",  # 检索的集合名称
            query=[random.random() for _ in range(10)],  # 10维随机查询向量（type: ignore忽略类型提示）
            limit=10,  # 返回最相似的前10个向量
            score_threshold=0.5  # 相似度得分阈值：只返回得分≥0.5的结果
        )
        # 打印检索结果中的向量点信息（包含ID、向量、得分等）
        print(res.points)
        for i in res.points:
            print(i)


    asyncio.run(test())
