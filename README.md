# 自制的轻小说文库的镜像（也许是）爬虫

## 所有数据均来自[轻小说文库](https://www.wenku8.net/)

- 支持小说信息的爬取
- 支持小说封面的爬取
- 支持小说内容全本爬取

# HOW TO USE

1. 克隆本仓库

```bash
git clone https://github.com/lawrance599/wenku8_mirror_spider.git
```

2. 下载依赖(确保已经安装了python)

```bash
cd wenku8_mirror_spider
pip install -r requirements.txt
```

3. 运行爬虫

```bash
cd ..
python run.py book #小说信息爬取
python run.py text #小说文本爬取
python run.py cover #小说封面爬取 
```

# <b>注意 ！！！<b>

- 请<b>不要<b>随意调整并发量和延迟以防对服务器造成伤害，<b>阻碍他人访问与网站正常运行!<b>-
- 爬虫采取数据库来存储信息，故需要将位于`model.py`中的`__engine_url`
  补充完整，详情可看模块处注释或自行前往<i>[sqlalchemy](https://www.sqlalchemy.org/)<i>查询

# todo

- [ ] 最新书目的自动跟进更新
- [ ] 定时更新
- [ ] 失败重试

# LICENSE

本项目遵守MIT LICENSE
