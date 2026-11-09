

import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker

from app.conf.app_config import app_config, DBConfig


class MysqlClientManager:
    '''
    SQLAlchemy的客户端
    '''
    def __init__(self,config:DBConfig):
        #Option[AsyncEngine]
        self.engine:None|AsyncEngine=None
        self.config=config
        pass

    def get_url(self):
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"

    def init_engine(self):
        #同步 create_engine
        #异步
        self.engine=create_async_engine(
            self.get_url(),
            pool_size = 10,
            pool_pre_ping = True
        )
        self.session_factory=async_sessionmaker(
            bind=self.engine,
            autoflush = True,
            expire_on_commit = False
        )
    async def close(self):
        await self.engine.dispose()

#这里全局单例
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)
meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)
if __name__ == '__main__':
    dw_mysql_client_manager.init_engine()
    async def test():
        async with dw_mysql_client_manager.session_factory() as session:
            # 执行sql查询
            result = await session.execute(text("select * from fact_order limit 10"))
            # 提取查询结果rows对象结构如：[(),(),()] 外层先转化成对象 取出所有的行  fetchall获取所有的行
            rows_tuple = result.fetchall()
            print(result)
            # 提取查询结果封装成字典结构如：[{},{},{}]（Result不可重放，由元组转换） 遍历行当中的数据然后.mapping建立对象映射表用dict转换
            rows = [dict(row._mapping) for row in rows_tuple]
            # 输出返回结果类型
            print(type(rows[0]))
            # 输出首行数据
            print(rows[0])
    asyncio.run(test())