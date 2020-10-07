# -*- coding: utf-8 -
from flask_sqlalchemy import SQLAlchemy
from .gt_flask import GtFlask
from .constant import VERSION
import logging.config
import os
import importlib

def create_log_path(log_path):
    """
    文件日志不会自动生成目录，只能先自行创建，否则日志报错
    """
    if not os.path.exists(log_path):
        os.makedirs(log_path)

def create_app(config):
    create_log_path(config.LOGGER_CONFIG['path'])
    logging.config.dictConfig(config.LOGGER_CONFIG)
    global app
    app = GtFlask(__name__)
    app.logger.info('---基础框架正在初始化中, 框架版本:V{}---'.format(VERSION))
    app.init_app()
    app.config.from_object(config)

    app.logger.info('初始化数据库...')
    db = SQLAlchemy(app)
    app.db = db

    from .processor import Processor
    app.logger.info('初始化任务处理器...')
    processor = Processor()
    processor.start()
    app.processor = processor

    if config.MODULES:
        app.modules = load_modules(config.MODULES)
    
    return app

def release_app():
    app.logger.info('---基础框架正在停止...')
    unload_modules()
    app.logger.info('停止任务处理器')
    app.processor.stop()
    app.logger.info('基础框架退出.')

def load_modules(modules_config):
    app.logger.info('开始加载模块...')
    modules = []

    for module in modules_config:
        name = module['name']
        app.logger.info('加载模块：{}'.format(name))

        try:
            inst = importlib.import_module(name, module['package'])
            init_app = getattr(inst, 'init_app')
            init_app(app)
            modules.append(inst)
        except:
            app.logger.error('Load Module [{}] Error.'.format(name), exc_info = True)

    return modules

def unload_modules():
    if not app.modules:
        return

    app.logger.info('开始卸载模块...')

    for module in app.modules:
        try:
            app.logger.info('卸载模块：{}'.format(module.__name__))
            uninit_app = getattr(module, 'uninit_app')
            uninit_app(app)
        except:
            app.logger.warning('Unload Module [{}] Error.'.format(module.__name__))
