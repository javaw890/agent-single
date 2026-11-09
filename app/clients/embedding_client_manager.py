from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpointEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddedClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.client:None|HuggingFaceEmbeddings=None
        self.config=config
        pass

    def _get_url(self):
        """
        私有方法：根据配置拼接嵌入服务的完整 URL

        Returns:
            str: 拼接后的嵌入式服务地址（http://host:port 格式）
        """
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        """
        初始化 HuggingFaceEndpointEmbeddings 客户端
        将拼接好的服务 URL 作为模型地址传入客户端
        """
        self.client=HuggingFaceEndpointEmbeddings(model=self._get_url())


# 创建 EmbeddedClientManager 实例（全局变量），传入应用配置中的嵌入服务配置
embedding_client_manager =EmbeddedClientManager(app_config.embedding)
# 主程序入口：测试嵌入式客户端功能
if __name__ == '__main__':
    client=EmbeddedClientManager(app_config.embedding)
    client.init()
    embed_query = client.client.embed_query("你好我是你爹")
    print(embed_query)