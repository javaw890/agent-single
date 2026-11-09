from elasticsearch import AsyncElasticsearch

from app.core.log import logger


class ValueEsReository:
    index_name="data-agent-values"
    es_index_mappings = {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
            "type": {"type": "keyword"},
            "column_id": {"type": "keyword"},
            "column_name": {"type": "keyword"},
            "table_id": {"type": "keyword"},
            "table_name": {"type": "keyword"},
        }
    }
    def __init__(self,client:AsyncElasticsearch ):
        self.client=client

    async def ensure_index(self):
        '''
        确保字段取值存储集合是否存在
        :return:
        '''
        if not await self.client.indices.exists(index=self.index_name):
            #不存在则创建
            await self.client.indices.create(
                index=self.index_name,
                mappings=self.es_index_mappings
            )
        logger.info("存储到es已完成")
