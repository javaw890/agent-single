# import sys
#
# from loguru import  logger
# #配置控制台输出方式
# logger.add(sys.stdout,format="{time}-{level}-{message}")
# #从文件中去输出日志  前面是相对路径 级别         最大多大
# logger.add("file_{time}.log",level="TRACE",rotation="100 MB")
# logger.info("info信息")
# logger.debug("22")
# #移除默认配置
# logger.remove() #清除上面的信息
# logger.error("22")
# logger.warning("22")
import asyncio
from contextvars import ContextVar


# 定义上下文变量request_id_ctx_var，用于在异步/多请求场景下存储和获取当前请求的唯一标识request_id
# 参数1："request_id" - 上下文变量的名称，用于标识该变量的用途
# 参数2：default=1 - 默认值，当未显式设置request_id时，获取到的值为1
request_id_ctx_var=ContextVar("request_id",default=1)

