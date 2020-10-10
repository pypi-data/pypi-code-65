#!/usr/bin/python
# -*- coding:UTF-8 -*-
from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time
# 首先构造一个SDK实例
api_sdk = K3CloudApiSdk('http://47.103.221.12:8126/k3cloud')
# 然后初始化SDK，需指定如下配置文件相关参数，否则会导致SDK初始化失败而无法使用：
# config_path:配置文件的相对或绝对路径，建议使用绝对路径
# config_node:配置文件中的节点名称
api_sdk.Init(config_path='E:\data\data\github\conf.ini', config_node='config')
# 比如查询“物料”(BD_MATERIAL)单据中的“物料名称”(FName)字段
print(api_sdk.ExecuteBillQuery({"FormId": "BD_MATERIAL", "FieldKeys": "FNumber,FName"}))
