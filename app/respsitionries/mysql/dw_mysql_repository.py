from sqlalchemy import text


class DwMysqlRepository:
    def __init__(self,session):
        self.session=session

    async def get_column_types(self, table_name):
        '''
        查询表中字段的类型 用原生的sql
        :param name:
        :return:
        '''
        sql=f"show columns from {table_name}"
        result = await self.session.execute(text(sql))
        #获取结果返回组装数据
        return {fetch.Field: fetch.Type for fetch in result.fetchall()}
    async def get_column_values(self, table_name:str, column_name:str,limit:int=10):
        '''
        查询指定字段的取值  执行sql+组装返回结果
        :param table_name:
        :param column_name:
        :return:  ["c001"]
        '''
        sql=f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        return result.scalars().fetchall()
