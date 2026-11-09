import asyncio
from argparse import ArgumentParser
from pathlib import Path

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.respsitionries.es.value_res_repository import ValueEsReository
from app.respsitionries.mysql.dw_mysql_repository import DwMysqlRepository
from app.respsitionries.mysql.meta_mysql_repository import  MetaKnowledgeRepository
from app.respsitionries.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


# 定义 build 函数，接收一个 Path 类型的参数 config_path，表示配置文件路径
async def build(config_path: Path):
    meta_mysql_client_manager.init_engine()
    dw_mysql_client_manager.init_engine()
    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()
    async with meta_mysql_client_manager.session_factory() as meta_session,dw_mysql_client_manager.session_factory() as dw_session:
        dw_mysql_repository=DwMysqlRepository(dw_session)
    # 打印日志，提示正在构建元知识
        meta_mysql_repository=MetaKnowledgeRepository(meta_session)
        column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client)
        value_es_repository = ValueEsReository(es_client_manager.client)
        #创建service对象
        meta_knowledge_service=MetaKnowledgeService(config_path,meta_mysql_repository,dw_mysql_repository=dw_mysql_repository,column_qdrant_repository=column_qdrant_repository,embedding_client=embedding_client_manager.client,value_es_repository=value_es_repository)
        await meta_knowledge_service.build()
    await meta_mysql_client_manager.close()
    await dw_mysql_client_manager.close()
    await qdrant_client_manager.close()
    await es_client_manager.close()

# 当脚本被直接运行时执行以下代码
if __name__ == '__main__':
    # 创建一个命令行参数解析器对象
    parser = ArgumentParser()
    # 添加一个可选参数，支持短选项 -c 和长选项 --conf
    # 该选项用于接收配置文件的路径
    parser.add_argument(
        '-c', '--conf',
        required=True,                              # 必须传，否则 argparse 直接报错退出
        help="配置文件路径，例如 config/meta_knowledge.yaml",
    )
    # 解析命令行传入的所有参数，并将结果存入 args 对象
    args = parser.parse_args()
    # 将命令行参数中获取的配置文件路径字符串，转换为 Path 对象
    config_path = Path(args.conf)
    # 调用 build 函数，传入解析后的配置文件路径
    asyncio.run(build(config_path))