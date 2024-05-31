# 使用 Docker 部署

构建 docker image

```bash
docker build -t zjooc .
```

运行 docker image

```bash
docker run -it --rm zjooc
```

# 本地部署

使用`pip install -r requirements.txt`安装依赖

运行`python tui.py`

- 不要在 pycharm 自带的终端中运行,TUI 会乱
