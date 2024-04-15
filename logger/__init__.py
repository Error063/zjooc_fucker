import logging

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 返回生产日志实例的方法
get_logger = logging.getLogger

if __name__ == '__main__':
    # 记录日志
    logger = get_logger()
    logger.debug("A debug message")
