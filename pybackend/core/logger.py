import os
import json
import logging
import logging.config
from datetime import datetime
# 简化版本，不使用 ContextManager
from typing import Dict, Any, Optional, Callable, Union, List


class Logger:
    init_log = False

    def __init__(self, dir_path, cfg_path, logger_name=__name__):
        self.dir_path = dir_path
        self.cfg_path = cfg_path
        if not Logger.init_log:
            Logger.setup_logging(self.dir_path, self.cfg_path)
            Logger.init_log = True
        self.logger = logging.getLogger(logger_name)

    @staticmethod
    def setup_logging(dir_path=None, config_path="config/log.json", default_level=logging.INFO, env_key="LOG_CFG"):
        # 如果没有指定dir_path，使用配置的日志目录
        if dir_path is None:
            try:
                from core.path_manager import get_path_manager
                path_manager = get_path_manager()
                dir_path = str(path_manager.log_dir)
            except ImportError:
                dir_path = "logs/"

        value = os.getenv(env_key, None)
        if value:
            path = value
        if os.path.exists(config_path):
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(config_path, "r") as f:
                config = json.load(f)
                config['handlers']['info_file_handler']['filename'] = os.path.join(dir_path, 'info.log')
                config['handlers']['error_file_handler']['filename'] = os.path.join(dir_path, 'error.log')
                logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)

    def get_log(self):
        return self.logger

    def debug(self, msg, *args):
        return self.logger.debug(msg, *args)

    def info(self, msg, *args):
        return self.logger.info(msg, *args)

    def warn(self, msg, *args):
        return self.logger.warning(msg, *args)

    def error(self, msg, *args):
        return self.logger.error(msg, *args)

    def exception(self, msg, *args):
        return self.logger.exception(msg, *args)

# 日志装饰器 - 用于标记需要记录详细日志的函数
def log_exception(
    service_name: Optional[str] = None
) -> Callable:
    """
    标记函数需要记录详细日志
    
    参数:
        service_name: 服务名称
    """
    def decorator(func: Callable) -> Callable:
        setattr(func, "__log_exception__", True)
        setattr(func, "__log_options__", {
            "service_name": service_name,
        })
        return func
    
    return decorator


