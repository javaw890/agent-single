import uuid

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.respsitionries.es.value_res_repository import ValueEsReository

from app.respsitionries.mysql.dw_mysql_repository import DwMysqlRepository
from app.respsitionries.mysql.meta_mysql_repository import MetaKnowledgeRepository
from app.respsitionries.qdrant.column_qdrant_repository import ColumnQdrantRepository


# 固定命名空间：UUID5 是"确定性"的，同一个 (字段, 文本类型) 每次都会算出同一个 id
# 这样重复执行 build 是覆盖写，而不是给 qdrant 无限追加重复向量
_POINT_NAMESPACE = uuid.UUID("9f1c2b7e-5a4d-4c2e-9b6f-1d3a8e7c0f42")


class MetaKnowledgeService:
    def __init__(self,config,meta_mysql_repository:MetaKnowledgeRepository,dw_mysql_repository:DwMysqlRepository,column_qdrant_repository:ColumnQdrantRepository,embedding_client:HuggingFaceEndpointEmbeddings,value_es_repository:ValueEsReository):
        self.meta_mysql_repository=meta_mysql_repository
        self.dw_mysql_repository=dw_mysql_repository
        self.column_qdrant_repository=column_qdrant_repository
        self.config=config
        self.embedding_client=embedding_client
        self.value_es_repository=value_es_repository


    async def build(self):
        # print(f"业务层接收到请求 配置文件{self.config}")
        #1加载配置config
        context = OmegaConf.load(self.config)
        schema=OmegaConf.structured(MetaConfig)
        meta_config:MetaConfig=OmegaConf.to_object(OmegaConf.merge(schema,context))
        print(meta_config)
        from app.core.log import logger
        logger.info("加载配置文件完成")
        #2.处理表信息 未来会增量新增的 #2.1保存表信息道meta数据库 构建向量索引（用来去检索） 构建全文索引 确保存储字段的向量集合存在  构建向量数据 存储qdrant
        if meta_config.tables:
            column_infos:list[ColumnInfoMySQL]=await  self._save_table_info_to_meta_db(meta_config)
            logger.info("保存表信息完成")
            await self._save_column_info_to_qdrant(column_infos)
            logger.info("为字段构建向量索引已完成")
            #构建全文索引es
            #确保存储的索引存在

            logger.info("开始构建全文索引")
            await self.value_es_repository.ensure_index()
        #3.处理指标信息  保存道meta数据库里面 构建向量索引（用来去检索） 构建全文索引






    async def _save_table_info_to_meta_db(self, meta_config):
        table_infos: list[TableInfoMySQL] = []
        # 创建字段信息封装列表
        column_infos: list[ColumnInfoMySQL] = []

        for table in meta_config.tables:
            table_info_mysql = TableInfoMySQL(
                id=table.name,
                name=table.name,
                role=table.role,
                description=table.description,
            )
            table_infos.append(table_info_mysql)

            # 查询表中所有字段的类型数据
            column_types: dict[str, str] = await self.dw_mysql_repository.get_column_types(table.name)
            for i in table.columns:
                column_values: list[str] = await self.dw_mysql_repository.get_column_values(table.name, i.name)
                column_infos.append(
                    ColumnInfoMySQL(
                        id=f"{table.name}.{i.name}",
                        name=i.name,
                        type=column_types.get(i.name),
                        role=i.role,
                        examples=column_values,
                        description=i.description,
                        alias=i.alias,
                        table_id=table.name,
                    )
                )

        async with self.meta_mysql_repository.session.begin():
            await self.meta_mysql_repository.save_table_infos(table_infos)
            await self.meta_mysql_repository.save_column_infos(column_infos)

        return column_infos

    @staticmethod
    def _make_point_id(column_id: str, kind: str) -> str:
        '''
        生成确定性的 point id
        同一个字段的同一种文本（name / description / alias:xxx）永远算出同一个 id，
        重复 build 时是覆盖写，不会把向量库撑爆
        :param column_id: 字段编号，例如 fact_order.order_id
        :param kind: 文本类型，name / description / alias:订单ID
        :return: 36 位 uuid 字符串
        '''
        return str(uuid.uuid5(_POINT_NAMESPACE, f"{column_id}|{kind}"))

    def _convert_column_info_from_mysql_to_qdrant(self,column_info:ColumnInfoMySQL)->ColumnInfoQdrant:
        '''
        转化
        :return:
        '''
        #ColumnInfoQdrant 是 TypedDict，只能关键字传参，不能按位置传
        return ColumnInfoQdrant(
            id=column_info.id,
            name=column_info.name,
            description=column_info.description,
            alias=column_info.alias or [],
            role=column_info.role,
            examples=column_info.examples or [],
            type=column_info.type,
            table_id=column_info.table_id,
        )

    async def _save_column_info_to_qdrant(self, column_infos:list[ColumnInfoMySQL]):
        await self.column_qdrant_repository.ensure_collection()
        points: list[dict] = []
        # 定义列表进行收集封装数据
        for column_info in column_infos:
            # 同一个字段的 name/description/alias 共用一份 payload
            payload = self._convert_column_info_from_mysql_to_qdrant(column_info)
            # name
            points.append({"id": self._make_point_id(column_info.id, "name"), "embedding_text": column_info.name,
                           "payload": payload})
            # description
            points.append(
                {"id": self._make_point_id(column_info.id, "description"), "embedding_text": column_info.description,
                 "payload": payload})
            # alias 可能是 None，不能直接 for 迭代
            for alias in column_info.alias or []:
                points.append({"id": self._make_point_id(column_info.id, f"alias:{alias}"), "embedding_text": alias,
                               "payload": payload})
        # 获取所有向量文本
        embedding_texts = [point["embedding_text"] for point in points]
        # 定义向量列表（注意：要和 points 一一对应，所以累积到这里）
        embeddings: list[list[float]] = []
        # 定义批次数据
        batch_size = 20
        for i in range(0, len(embedding_texts), batch_size):
            # 转换向量
            batch_embeddings = await self.embedding_client.aembed_documents(embedding_texts[i:i + batch_size])
            # 保存向量
            embeddings.extend(batch_embeddings)
        # 获取所有的id
        ids = [point["id"] for point in points]
        payloads = [point["payload"] for point in points]
        await self.column_qdrant_repository.upsert_column_embeddings(ids, embeddings, payloads)

