FROM elasticsearch:8.19.10

USER root
#ik比较友好的 copy
COPY plugins/elasticsearch-analysis-ik-8.19.10.zip /tmp/
#安装插件
RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch \
    file:///tmp/elasticsearch-analysis-ik-8.19.10.zip
#设置权限
RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/plugins
#切换到elasticsearch用户 用的时候必须是用这个用户
USER elasticsearch
