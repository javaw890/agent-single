from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL


class MetaKnowledgeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_table_infos(self, table_infos: list[TableInfoMySQL]) -> None:
        """批量写入表元数据，主键冲突时改为更新（幂等，可重复执行）"""
        if not table_infos:
            return
        rows = [
            {
                "id": t.id,
                "name": t.name,
                "role": t.role,
                "description": t.description,
            }
            for t in table_infos
        ]

        stmt = insert(TableInfoMySQL).values(rows)
        stmt = stmt.on_duplicate_key_update(
            name=stmt.inserted.name,
            role=stmt.inserted.role,
            description=stmt.inserted.description,
        )
        await self.session.execute(stmt)

    async def save_column_infos(self, column_infos: list[ColumnInfoMySQL]) -> None:
        """批量写入列元数据，主键冲突时改为更新（幂等，可重复执行）"""
        if not column_infos:
            return

        rows = [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "role": c.role,
                "examples": c.examples,
                "description": c.description,
                "alias": c.alias,
                "table_id": c.table_id,
            }
            for c in column_infos
        ]

        stmt = insert(ColumnInfoMySQL).values(rows)
        stmt = stmt.on_duplicate_key_update(
            name=stmt.inserted.name,
            type=stmt.inserted.type,
            role=stmt.inserted.role,
            examples=stmt.inserted.examples,
            description=stmt.inserted.description,
            alias=stmt.inserted.alias,
            table_id=stmt.inserted.table_id,
        )
        await self.session.execute(stmt)
