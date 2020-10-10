#!/usr/bin/python
# -*- coding:UTF-8 -*-
#以下为生产订单主要内容简称mo
from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time
import json
from k3cloud_webapi_sdk.main import K3CloudApiSdk
import json
import pymssql
import datetime
from collections.abc import Iterable
from collections.abc import Iterator

#生产订单的测试订单
# 以下为最小的测试数据，非导入格式
def mo_testData():
    res = {'FId': 135534, 'FDate': '2020-10-06T00:00:00', 'FPrdOrgNumber': '100.01', 'FDescription': '', 'F_NLJ_delivery': ' ',
           'F_NLJ_calcBatch': False, 'F_NLJ_insideID': False, 'FProductType': ['1'], 'FMaterialNumber': ['1.1.01.1.03.0019'],
           'FUnitNumber': ['0101'], 'FBaseUnitNumber': ['0101'], 'FQty': [27000.0], 'FStockNumber': ['01.001'],
           'F100001_Id': [0], 'F100001': [None], 'F100004_Id': [100124], 'F100004': [{'Id': 100124, 'Number': '0105065', 'MultiLanguageText': [{'PkId': 100124, 'LocaleId': 2052, 'Name': 'A06-1a'}], 'Name': [{'Key': 2052, 'Value': 'A06-1a'}]}], 'F100005_Id': [0], 'F100005': [None], 'F100006_Id': [0], 'F100006': [None], 'F100007_Id': [0], 'F100007': [None], 'F100008_Id': [0], 'F100008': [None], 'F100009_Id': [0], 'F100009': [None], 'F100010_Id': [0], 'F100010': [None], 'F100012_Id': [0], 'F100012': [None],
           'FStockLocId': [{'FSTOCKLOCID__FF100001': {'FNumber': ''}, 'FSTOCKLOCID__FF100004': {'FNumber': '0105065'}, 'FSTOCKLOCID__FF100005': {'FNumber': ''}, 'FSTOCKLOCID__FF100006': {'FNumber': ''}, 'FSTOCKLOCID__FF100007': {'FNumber': ''}, 'FSTOCKLOCID__FF100008': {'FNumber': ''}, 'FSTOCKLOCID__FF100009': {'FNumber': ''}, 'FSTOCKLOCID__FF100010': {'FNumber': ''}, 'FSTOCKLOCID__FF100012': {'FNumber': ''}}],
           'FWorkShopNumber': ['19.06'], 'FRequestOrgNumber': ['100.01'], 'FBomVerNumber': ['1.1.01.1.03.0019_V1.1'], 'FIsBackFlush': [True],
           'FStockInOrgNumber': ['100.01'], 'F_NLJ_SONote': [' '], 'F_NLJ_SOBODYNOTE2': [' '], 'F_NLJ_BatchNote': [' '],
           'F_NLJ_LableItemModel': ['分离胶-促凝管'], 'F_NLJ_LableItemModel_KWSJ': [' '], 'F_NLJ_PrdColor': ['黄色'], 'F_NLJ_Additive': ['分离胶-促凝剂'],
           'F_NLJ_BloodCollectionVol': ['3ml'], 'F_NLJ_CollectionVol': [' '], 'F_NLJ_Reagent': [' '], 'F_NLJ_TubeModel': ['Φ13×75mm'],
           'F_NLJ_TubeMaterial': ['玻璃'], 'F_NLJ_QtyShowText': ['100支/盘×18盘'], 'F_NLJ_PkgQty': ['1800'], 'F_NLJ_ApplyAltitude': ['1500米'],
           'F_NLJ_LabelNote1': [' '], 'F_NLJ_SpecialOR': [' '], 'F_NLJ_SterilizationMethod': [' ']}

    return(res)
#定义测试数据的字段列表
def mo_testData_keys():
    data = mo_testData()
    res = list(data.keys())
    return(res)



#针对仓位进行处理
def stockPlace_keyValue():
    res = ['F100001_Id','F100001','F100004_Id','F100004','F100005_Id','F100005','F100006_Id','F100006',
'F100007_Id','F100007','F100008_Id','F100008','F100009_Id','F100009','F100010_Id','F100010','F100012_Id','F100012']
    return (res)
def stockPlace_key():
    res = ['F100001_Id','F100004_Id','F100005_Id','F100006_Id',
'F100007_Id','F100008_Id','F100009_Id','F100010_Id','F100012_Id']
    return(res)
def stockPlace_value():
    res = ['F100001','F100004','F100005','F100006',
'F100007','F100008','F100009','F100010','F100012']
    return(res)
# 定义生产订单表体的模板
def stockPlace_tpl():
    res = {
        "FSTOCKLOCID__FF100001": {
            "FNumber": ""
        },
        "FSTOCKLOCID__FF100004": {
            "FNumber": ""
        },
        "FSTOCKLOCID__FF100005": {
            "FNumber": ""
        },
        "FSTOCKLOCID__FF100006": {
            "FNumber": ""
        },
        "FSTOCKLOCID__FF100007": {
            "FNumber": ""
        },
        "FSTOCKLOCID__FF100008": {
            "FNumber": ""
        },
        "FSTOCKLOCID__FF100009": {
            "FNumber": ""
        },
        "FSTOCKLOCID__FF100010": {
            "FNumber": ""
        },
        "FSTOCKLOCID__FF100012": {
            "FNumber": ""
        }
    }
    return(res)
# 定义模板上的所有键值
def stockPlace_tpl_keys():
    data = stockPlace_tpl()
    res = list(data.keys())
    return(res)
#定义生产订单数据包解析辅助函数
def formatter_mo_bill(r):
    data_mo_src = json.loads(r)
    # print(data_mo_src) #显示结果的原因内容
    # 针对结果进行处理
    # 如果可以返回数据
    if data_mo_src["Result"]["ResponseStatus"] is None:
        mo_bill_src = data_mo_src['Result']['Result']
        # 返回数据
        # 将结果存储在字典中
        res = {}
        res['FId'] = mo_bill_src['Id']  # 单据内码
        res['FDate'] = mo_bill_src['Date']  # 单据日期
        res['FPrdOrgNumber'] = mo_bill_src['PrdOrgId']['Number']  # 生产组织代码
        # 表头备注
        if len(mo_bill_src['Description']) > 0:
            res['FDescription'] = mo_bill_src['Description'][0]['Value']
        else:
            res['FDescription'] = ''
        # 出货安排
        res['F_NLJ_delivery'] = mo_bill_src['F_NLJ_delivery']
        # 出口单据批号带入
        res['F_NLJ_calcBatch'] = mo_bill_src['F_NLJ_calcBatch']
        # 国内订单批号带入
        res['F_NLJ_insideID'] = mo_bill_src['F_NLJ_insideID']
        # 数据平台的状态
        res['F_NLJ_DataPlatformStatus'] = mo_bill_src['F_NLJ_DataPlatformStatus']
        #针对生产订单的表体进行处理，支持多列
        body = mo_bill_src['TreeEntity']
        # 针对生产订单表体
        # 使用列表表达式针对每个字段进行处理
        res['FProductType'] = [row['ProductType'] for row in body] #产品类型
        res['FMaterialNumber'] = [row['MaterialId']['Number'] for row in body] #物料编码
        # ---------以下为单位相关信息---------
        res['FUnitNumber'] = [row['UnitId']['Number'] for row in body] #物料单位
        res['FBaseUnitNumber'] = [row['BaseUnitId']['Number'] for row in body] #物料基本单位
        # ----------End for FUnit--------------------
        res['FQty'] = [row['Qty'] for row in body] # 生产数量
        # 以下为FQty相关的数量，默认保持一致
        # res['FBaseUnitQty'] = [row['BaseUnitQty'] for row in body] #基本单位数量
        # res['FBaseYieldQty'] = [row['BaseYieldQty'] for row in body] # 基础产出数 默认与FQty相同所以放在一起
        # res['FBaseStockInLimitH'] = [row['BaseStockInLimitH'] for row in body] #入库上限{基本单位数量）默认与FQty一致
        # res['FStockInLimitH'] = [row['StockInLimitH'] for row in body] # 入库上限(常用单位)
        # res['FBaseStockInLimitL'] = [row['BaseStockInLimitL'] for row in body] #入库下限(基本单位数量) 默认为FQty一致
        # res['FStockInLimitL'] =  [row['StockInLimitL'] for row in body]  #入库下限(常用单位)
        # res['FBaseNoStockInQty'] = [row['BaseNoStockInQty'] for row in body] # 未入库数量，默认为FQty
        # res['FNoStockInQty'] = [row['NoStockInQty'] for row in body]  #未入库数量,默认为FQty
        # -------------------End for FQty------------------------------------
        # 仓库仓位相关信息
        res['FStockNumber'] = [row['StockId']['Number'] for row in body] #表体仓库默认带到生产入库单上
        stockPlaceSet = [row['StockLocId'] for row in body] #仓位信息
        #print(stockPlaceSet)

        #print(stockPlaceSet[0] is None)
        #定义仓位集
        #获取所有的键值对

        #针对数据进行格式化处理
        stockPlaceSet2 = []
        for sp_row in stockPlaceSet:
            if sp_row is None:
                FStockLocId_src = stockPlace_tpl()
                # FStockLocId_src = None
                stockPlaceSet2.append(FStockLocId_src)
            else:
                sp_keyValue = stockPlace_keyValue()
                sp_count = len(sp_keyValue)
                sp_dict = {}
                for idx in range(sp_count):
                    # print(idx)
                    #res[sp_keyValue[idx]] = [row[sp_keyValue[idx]] for row in stockPlaceSet]
                    sp_dict[sp_keyValue[idx]] = sp_row[sp_keyValue[idx]]
                FStockLocId_src = stockPlace_tpl()
                # 针对数据进行处理
                sp_id = stockPlace_key()
                # print(sp_id)
                sp_value = stockPlace_value()
                sp_combo = stockPlace_tpl_keys()
                sp_combo_count = len(sp_combo)
                for j in range(sp_combo_count):
                    # print('bug')
                    if sp_dict[sp_id[j]] > 0:
                        FStockLocId_src[sp_combo[j]]['FNumber'] = sp_dict[sp_value[j]]['Number']
                # 添加数据
                stockPlaceSet2.append(FStockLocId_src)

        res['FStockLocId'] = stockPlaceSet2
        # print('bug')
        print(stockPlaceSet2)

        # ---------end for 仓库仓位
        res['FWorkShopNumber'] = [row['WorkShopID']['Number'] for row in body] #生产车间代码
        res['FRequestOrgNumber'] = [row['RequestOrgId']['Number'] for row in body] # 需求组织
        res['FBomVerNumber'] = [row['BomId']['Number'] for row in body] # BOM版本号
        res['FIsBackFlush'] = [row['ISBACKFLUSH'] for row in body] #表体是否倒冲
        res['FStockInOrgNumber'] = [row['StockInOrgId']['Number'] for row in body] # 生产入库组织
        #定义自定义相关字段
        res['F_NLJ_SONote'] = [row['F_NLJ_SONote'] for row in body] # 销售订单表头备注
        res['F_NLJ_SOBODYNOTE2'] = [row['F_NLJ_SOBODYNOTE2'] for row in body] #销售订单表体备注
        res['F_NLJ_BatchNote'] =[row['F_NLJ_BatchNote'] for row in body] #批号备注
        res['F_NLJ_LableItemModel'] =[row['F_NLJ_LableItemModel'] for row in body] #标签规格
        res['F_NLJ_LableItemModel_KWSJ'] = [row['F_NLJ_LableItemModel_KWSJ'] for row in body] #标签规格(康为世纪)
        res['F_NLJ_PrdColor'] = [row['F_NLJ_PrdColor'] for row in body] #色标
        res['F_NLJ_Additive'] = [row['F_NLJ_Additive'] for row in body] #添加剂
        res['F_NLJ_BloodCollectionVol'] = [row['F_NLJ_BloodCollectionVol'] for row in body] #采血量
        res['F_NLJ_CollectionVol'] = [row['F_NLJ_CollectionVol'] for row in body] #采集量
        res['F_NLJ_Reagent'] = [row['F_NLJ_Reagent'] for row in body] #试剂量
        res['F_NLJ_TubeModel'] = [row['F_NLJ_TubeModel'] for row in body] #管体规格
        res['F_NLJ_TubeMaterial'] = [row['F_NLJ_TubeMaterial'] for row in body] #管体材质
        res['F_NLJ_QtyShowText'] = [row['F_NLJ_QtyShowText'] for row in body] #标签数量
        res['F_NLJ_PkgQty'] = [row['F_NLJ_PkgQty'] for row in body] #包装数量
        res['F_NLJ_ApplyAltitude'] = [row['F_NLJ_ApplyAltitude'] for row in body] #适用海拔
        res['F_NLJ_LabelNote1'] = [row['F_NLJ_LabelNote1'] for row in body] #标签备注1
        res['F_NLJ_SpecialOR'] = [row['F_NLJ_SpecialOR'] for row in body] #订单特殊要求
        res['F_NLJ_SterilizationMethod'] = [row['F_NLJ_SterilizationMethod'] for row in body] #灭菌方式

    else:
        res = None
    return (res)
# 建立生产订单数据包格式化函数
def data_mo_bill(FBillNo='MO033489'):
    data = {
        "CreateOrgId": 0,
        "Number": FBillNo,
        "Id": ""
    }
    return(data)

# 建立生产订单的数据体
def data_moEntry_upload(data=mo_testData()):
    #使用物料编码进行判断依据
    # print('bug data')
    # print(data['FStockLocId'])
    material_count =len(data['FMaterialNumber'])
    res = []
    for i in range(material_count):
        row_tpl = {
            "FEntryId": 0,
            "FProductType": data['FProductType'][i],
            "FMaterialId": {
                "FNumber": data['FMaterialNumber'][i]
            },
            "FUnitId": {
                "FNumber": data['FUnitNumber'][i]
            },
            "FQty": data['FQty'][i],
            "FYieldQty": 0,
            "FWorkShopID": {
                "FNumber": data['FWorkShopNumber'][i]
            },
            "FPlanStartDate": data['FDate'],
            "FPlanFinishDate": data['FDate'],
            "FRequestOrgId": {
                "FNumber": data['FRequestOrgNumber'][i]
            },
            "FBomId": {
                "FNumber": data['FBomVerNumber'][i]
            },
            "FISBACKFLUSH": data['FIsBackFlush'][i],
            "FLot": {
                "FNumber": ""
            },
            "FStockInOrgId": {
                "FNumber": data['FStockInOrgNumber'][i]
            },
            "FBaseYieldQty": data['FQty'][i],
            "FReqType": "1",
            "FPriority": 0,
            "FSTOCKREADY": 0,
            "FBaseStockReady": 0,
            "FBaseRepairQty": 0,
            "FRepairQty": 0,
            "FBaseStockInScrapSelQty": 0,
            "FStockInScrapSelQty": 0,
            "FBaseStockInScrapQty": 0,
            "FStockInScrapQty": 0,
            "FBaseRptFinishQty": 0,
            "FRptFinishQty": 0,
            "FMTONO": "",
            "FStockInFailSelAuxQty": 0,
            "FStockInUlRatio": 0,
            "FAuxPropId": {
                "FAUXPROPID__FF100001": {
                    "FNumber": ""
                }
            },
            "FInStockOwnerTypeId": "",
            "FBaseStockInLimitH": data['FQty'][i],
            "FInStockOwnerId": {
                "FNumber": ""
            },
            "FInStockType": "",
            "FStockInLlRatio": 0.0,
            "FCheckProduct": "false",
            "FOutPutOptQueue": "",
            "FBaseStockInLimitL": data['FQty'][i],
            "FBaseUnitQty": data['FQty'][i],
            "FRepQuaSelAuxQty": 0,
            "FRepQuaAuxQty": 0,
            "FRepFailSelAuxQty": 0.0,
            "FStockInReMadeSelQty": 0.0,
            "FMemoItem": "",
            "FRoutingId": {
                "FNumber": ""
            },
            "FRepFailAuxQty": 0,
            "FStockInQuaAuxQty": 0.0,
            "FStockInQuaSelAuxQty": 0.0,
            "FStockInFailAuxQty": 0.0,
            "FStockInQuaSelQty": 0.0,
            "FStockInQuaQty": 0.0,
            "FBaseUnitId": {
                "FNumber": data['FBaseUnitNumber'][i]
            },
            "FStockInFailSelQty": 0.0,
            "FStockId": {
                "FNumber": data['FStockNumber'][i]
            },
            "FStockInFailQty": 0.0,
            "FRepQuaSelQty": 0.0,
            "FStockLocId": data['FStockLocId'][i],
            "FRepQuaQty": 0.0,
            "FStockInLimitH": data['FQty'][i],
            "FRepFailSelQty": 0.0,
            "FRepFailQty": 0.0,
            "FStockInLimitL": data['FQty'][i],
            "FOperId": 0,
            "FProcessId": {
                "FNumber": ""
            },
            "FCostRate": 100.000000,
            "FCreateType": "1",
            "FYieldRate": 100.0000000000,
            "FGroup": 1,
            "FNoStockInQty": data['FQty'][i],
            "FParentRowId": "",
            "FRowExpandType": 0,
            "FBaseNoStockInQty": data['FQty'][i],
            "FRowId": "",
            "FScheduleSeq": 0.0,
            "FREMWorkShopId": {
                "FNUMBER": ""
            },
            "FCloseType": "",
            "FScheduleStartTime": "1900-01-01",
            "FForceCloserId": {
                "FUserID": ""
            },
            "FScheduleFinishTime": "1900-01-01",
            "FSNUnitID": {
                "FNumber": ""
            },
            "FSNQty": 0.0,
            "FScheduleProcSplit": 0,
            "FReStkQuaQty": 0,
            "FBaseReStkQuaQty": 0,
            "FReStkReMadeQty": 0,
            "FReStkFailQty": 0,
            "FStockInReMadeQty": 0,
            "FBaseReStkFailQty": 0,
            "FBaseReStkReMadeQty": 0,
            "FBaseReStkScrapQty": 0,
            "FReStkScrapQty": 0,
            "FScheduleStatus": "",
            "FPickMtrlStatus": "1",
            "FISNEWLC": 0,
            "FSrcSplitSeq": 0,
            "FSrcSplitBillNo": "",
            "FSrcSplitEntryId": 0,
            "FSrcSplitId": 0,
            "FSRCBOMENTRYID": 0,
            "FMOChangeFlag": "false",
            "F_NLJ_ProdBatchNo": "",
            "FBaseStockInReMadeSelQty": 0,
            "F_NLJ_DEFAULTStockPlace": {
                "F_NLJ_DEFAULTSTOCKPLACE__FF100001": {
                    "FNumber": ""
                },
                "F_NLJ_DEFAULTSTOCKPLACE__FF100004": {
                    "FNumber": ""
                },
                "F_NLJ_DEFAULTSTOCKPLACE__FF100005": {
                    "FNumber": ""
                },
                "F_NLJ_DEFAULTSTOCKPLACE__FF100006": {
                    "FNumber": ""
                },
                "F_NLJ_DEFAULTSTOCKPLACE__FF100007": {
                    "FNumber": ""
                },
                "F_NLJ_DEFAULTSTOCKPLACE__FF100008": {
                    "FNumber": ""
                },
                "F_NLJ_DEFAULTSTOCKPLACE__FF100009": {
                    "FNumber": ""
                },
                "F_NLJ_DEFAULTSTOCKPLACE__FF100010": {
                    "FNumber": ""
                },
                "F_NLJ_DEFAULTSTOCKPLACE__FF100012": {
                    "FNumber": ""
                }
            },
            "F_NLJ_SONote": data['F_NLJ_SONote'][i],
            "F_NLJ_SOBodyNote": "",
            "FCloseReason": "",
            "F_NLJ_SOBODYNOTE2": data['F_NLJ_SOBODYNOTE2'][i],
            "F_NLJ_BatchNote": data['F_NLJ_BatchNote'][i],
            "FIsFirstInspect": "false",
            "F_NLJ_LastPickDate": "1900-01-01",
            "FFirstInspectStatus": "",
            "F_NLJ_PrdStockDate": "1900-01-01",
            "F_NLJ_UnPickInfo": "",
            "F_NLJ_FirstDate": "1900-01-01",
            "F_NLJ_DirectPickFlag": "false",
            "F_NLJ_Combo": "",
            "F_NLJ_LableItemModel": data['F_NLJ_LableItemModel'][i],
            "F_NLJ_LableItemModel_KWSJ": data['F_NLJ_LableItemModel_KWSJ'][i],
            "F_NLJ_PrdColor": data['F_NLJ_PrdColor'][i],
            "F_NLJ_Additive": data['F_NLJ_Additive'][i],
            "F_NLJ_BloodCollectionVol": data['F_NLJ_BloodCollectionVol'][i],
            "F_NLJ_CollectionVol": data['F_NLJ_CollectionVol'][i],
            "F_NLJ_Reagent": data['F_NLJ_Reagent'][i],
            "F_NLJ_TubeModel": data['F_NLJ_TubeModel'][i],
            "F_NLJ_TubeMaterial": data['F_NLJ_TubeMaterial'][i],
            "F_NLJ_QtyShowText": data['F_NLJ_QtyShowText'][i],
            "F_NLJ_PkgQty": data['F_NLJ_PkgQty'][i],
            "F_NLJ_ApplyAltitude": data['F_NLJ_ApplyAltitude'][i],
            "F_NLJ_SterilizationMethod": data['F_NLJ_SterilizationMethod'][i],
            "F_NLJ_LabelNote1": data['F_NLJ_LabelNote1'][i],
            "F_NLJ_SpecialOR": data['F_NLJ_SpecialOR'][i],
            "FSerialSubEntity": [
                {
                    "FDetailID": 0,
                    "FSNQty1": 0,
                    "FSerialNo": "",
                    "FSerialId": {
                        "FNUMBER": ""
                    },
                    "FSNRptSelQty": 0,
                    "FSNStockInSelQty": 0,
                    "FSerialNote": "",
                    "FBaseSNQty": 0,
                    "FBaseSNRptSelQty": 0,
                    "FBaseSNStockInSelQty": 0
                }
            ]
        }
        res.append(row_tpl)
    return(res)


#生产订单的上传格式
def data_mo_upload(data=mo_testData(),FBillType="SCDD01_SYS",is_new_bill=False):
    var_id = 0
    data_status = ''
    if is_new_bill:
        var_id = 0
        data_status = mo_actionTime('自动新增')
    else:
        var_id = data['FId']
        data_status = mo_actionTime()
    res = {
    "Creator": "",
    "NeedUpDateFields": [],
    "NeedReturnFields": [],
    "IsDeleteEntry": "true",
    "SubSystemId": "",
    "IsVerifyBaseDataField": "false",
    "IsEntryBatchFill": "true",
    "ValidateFlag": "true",
    "NumberSearch": "true",
    "InterationFlags": "",
    "Model": {
        "FID": var_id,
        "FBillType": {
            "FNUMBER": FBillType
        },
        "FDate": data['FDate'],
        "FPrdOrgId": {
            "FNumber": data['FPrdOrgNumber']
        },
        "FWorkShopID0": {
            "FNumber": ""
        },
        "FWorkGroupId": {
            "FNumber": ""
        },
        "FPlannerID": {
            "FNumber": ""
        },
        "FOwnerTypeId": "BD_OwnerOrg",
        "FIsRework": "false",
        "FBusinessType": "1",
        "FOwnerId": {
            "FNumber": ""
        },
        "FTrustteed": "false",
        "FDescription": data['FDescription'],
        "FIsEntrust": "false",
        "FEnTrustOrgId": {
            "FNumber": ""
        },
        "FPPBOMType": "1",
        "FIssueMtrl": "false",
        "F_NLJ_Text": "",
        "F_NLJ_ActualDate": data['FDate'],
        "F_NLJ_calcBatch": data['F_NLJ_calcBatch'],
        "F_NLJ_RDStatus": "",
        "F_NLJ_insideID": data['F_NLJ_insideID'],
        "F_NLJ_delivery": data['F_NLJ_delivery'],
        "F_NLJ_DataPlatformStatus": data_status,
        "FTreeEntity": data_moEntry_upload(data),
        "FScheduledEntity": [
            {
                "FEntryID": 0
            }
        ]
    }
    }
    return(res)

# 生产订单的单据类型的名称
def mo_billType_rpt_common():
    res = mo_billTypeList()[0]
    res = mo_billType_getNumber(res)
    return(res)
def mo_billType_rpt_reWork():
    res = mo_billTypeList()[1]
    res = mo_billType_getNumber(res)
    return(res)
def mo_billType_stockIn_common():
    res = mo_billTypeList()[2]
    res = mo_billType_getNumber(res)
    return(res)
def mo_billType_stockIn_zz():
    res = mo_billTypeList()[3]
    res = mo_billType_getNumber(res)
    return(res)
def mo_billType_stockIn_reWork():
    res = mo_billTypeList()[4]
    res = mo_billType_getNumber(res)
    return(res)
def mo_billTypeList():
    connect = pymssql.connect('115.159.201.178', 'sa', 'Hoolilay889@', 'kdc')  # 服务器名,账户,密码,数据库名
    if connect:
        print("连接成功!")
        cursor = connect.cursor()  # 创建一个游标对象,python里的sql语句都要通过cursor来执行
        # 1 插入数据表
        sql = "select FBillTypeName  from t_md_billType where FBillName='生产订单' order by FBillTypeNumber"
        # print(sql)
        cursor.execute(sql)  # 执行sql语句
        row = cursor.fetchall()  # 读取查询结果,
        if len(row) > 0:
            res = [item[0] for item in row]
        else:
            res = None
    else:
        print('连接不成功')
        res = None

    return (res)

# 生产订单的单据类型
def mo_billType_getNumber(FBillName='汇报入库-普通生产'):
    connect = pymssql.connect('115.159.201.178', 'sa', 'Hoolilay889@', 'kdc')  # 服务器名,账户,密码,数据库名
    if connect:
        print("连接成功!")
    cursor = connect.cursor()  # 创建一个游标对象,python里的sql语句都要通过cursor来执行
    # 1 插入数据表
    sql = "select FBillTypeNumber from t_md_billType where FBillTypeName='" + FBillName+"' and FBillName='生产订单'"
    # print(sql)
    cursor.execute(sql)  # 执行sql语句
    row = cursor.fetchall()  # 读取查询结果,
    if len(row) > 0:
        res = row[0][0]
    else:
        res = None
    return(res)
# 生产订单查看
def mo_view(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',FBillNo='MO033489'):
    #创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    #针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    #针对数据包进行格式化处理
    data = data_mo_bill(FBillNo=FBillNo)
    #调用金蝶接口
    r = api_sdk.View("PRD_MO",data = data)
    # print('生产订单原始数据:')
    # print(r)
    #针对接口进行格式化
    res = formatter_mo_bill(r)
    # 返回结果
    return (res)
# 创建新的生产订单
def mo_create(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              data=mo_testData(),FBillType="SCDD01_SYS"):
    #创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    #针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    #针对数据包进行格式化处理
    data_create = data_mo_upload(data=data,FBillType=FBillType,is_new_bill=True)
    #调用金蝶接口
    r = api_sdk.Save("PRD_MO", data_create)
    res = json.loads(r)
    # 返回结果
    return (res)
# 复制产生新的生产订单
def mo_copy(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              FBillNo='MO033489',FBillType="SCDD01_SYS"):
    #创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    #针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    #针对数据包进行格式化处理
    data_copy = mo_view(config_path=config_path,kdc_url=kdc_url,FBillNo=FBillNo)
    #调用金蝶接口
    res = mo_create(config_path=config_path,kdc_url=kdc_url,data=data_copy,FBillType=FBillType)
    # 返回结果
    return (res)
# 修改现有的生产订单
def mo_update(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              data=mo_testData(),FBillType="SCDD01_SYS"):
    #创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    #针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    #针对数据包进行格式化处理
    data_update = data_mo_upload(data=data,FBillType=FBillType,is_new_bill=False)
    #调用金蝶接口
    r = api_sdk.Save("PRD_MO", data_update)
    res = json.loads(r)
    # 后续需要对res进行分析
    # 返回结果
    return (res)
# 重新保存生产订单
def mo_actionTime(action='自动重新保存'):
    str_time = str(datetime.datetime.now())
    res = action + str_time[:19]
    return(res)

def mo_reSave(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              FBillNo='MO033489',FBillType="SCDD01_SYS"):
    #创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    #针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    #针对数据包进行格式化处理
    data_copy = mo_view(config_path=config_path,kdc_url=kdc_url,FBillNo=FBillNo)
    #调用金蝶接口
    res = mo_update(config_path=config_path,kdc_url=kdc_url,data=data_copy,FBillType=FBillType)
    # 返回结果
    return (res)
# 批量保存生产订单
def mo_reSave_batch(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              FBillNoList=['MO033489','MO033561'],FBillType="SCDD01_SYS"):
    if FBillNoList is None:
        res = None
    else:
        res = []
        for FBillNo in FBillNoList:
            msg = mo_reSave(config_path=config_path, kdc_url=kdc_url, FBillNo=FBillNo, FBillType=FBillType)
            res.append(msg)
    return(res)




# 查看创建或重新审核状态的生产订单
def mo_list_newToDo(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud'):
    # 创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    # 针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    data = {
    "FormId": "PRD_MO",
    "FieldKeys": "FBillNo",
    "FilterString": "len(F_NLJ_DataPlatformStatus) <4 and  (FDocumentStatus ='A' or FDocumentStatus ='D')",
    "OrderString": "",
    "TopRowCount": 0,
    "StartRow": 0,
    "Limit": 0
    }
    r = api_sdk.ExecuteBillQuery(data = data)
    r = json.loads(r)
    #print(type(r))
    if len(r) >0:
        res = [row[0] for row in r]
    else:
        res = None
    return (res)

# 批量保存生产订单自动重新保存未审核或重新审核的单据
def mo_reSave_auto(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              FBillType="SCDD01_SYS"):
    mydata = mo_list_newToDo(config_path=config_path,kdc_url=kdc_url)
    res = mo_reSave_batch(config_path=config_path,kdc_url=kdc_url,FBillNoList=mydata,FBillType=FBillType)
    return(res)

#生产订单提交
def mo_submit(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              FBillList=['MO033473']):
    # 创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    # 针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    data = {
        "CreateOrgId": 0,
        "Numbers": FBillList,
        "Ids": "",
        "SelectedPostId": 0,
        "NetworkCtrl": ""
    }
    r = api_sdk.Submit('PRD_MO', data)
    res = json.loads(r)
    return(res)
# 生产订单审核
def mo_audit(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              FBillList=['MO033473']):
    # 创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    # 针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    data = {
    "CreateOrgId": 0,
    "Numbers": FBillList,
    "Ids": "",
    "InterationFlags": "",
    "NetworkCtrl": ""
    }
    r = api_sdk.Audit('PRD_MO', data)
    res = json.loads(r)
    return(res)
# 生产订单反审核
def mo_unAudit(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              FBillList=['MO033473']):
    # 创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    # 针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    data = {
    "CreateOrgId": 0,
    "Numbers": FBillList,
    "Ids": "",
    "InterationFlags": "",
    "NetworkCtrl": ""
    }
    r = api_sdk.UnAudit('PRD_MO', data)
    res = json.loads(r)
    return(res)
# 生产订单删除
def mo_delete(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              FBillList=['MO033473']):
    # 创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    # 针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    data = {
    "CreateOrgId": 0,
    "Numbers": FBillList,
    "Ids": "",
    "NetworkCtrl": ""
    }
    r = api_sdk.Delete('PRD_MO', data)
    res = json.loads(r)
    return(res)
# 生产订单下达
def mo_release(config_path='D:\data\py_data\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',
              FBillList=['MO033473']):
    # 创建客户端
    api_sdk = K3CloudApiSdk(kdc_url)
    # 针对客户端进行初始化处理
    api_sdk.Init(config_path=config_path, config_node='config')
    data = {
    "CreateOrgId": 0,
    "Numbers": FBillList,
    "Ids": "",
    "NetworkCtrl": ""
    }
    r = api_sdk.ExcuteOperation("PRD_MO","ToRelease",data)
    res = json.loads(r)
    return(res)















#测试区域
if __name__ == '__main__':
    # print(stockPlace_keyValue())
    # print(stockPlace_key())
    # print(stockPlace_value())
    # print(stockPlace_tpl_keys())
    # 生产订单查看单据
    #print(mo_view())
    # print(mo_view(FBillNo='MO032949'))

    # print(mo_testData())
    # print(mo_testData_keys())
    #print(data_mo_upload( is_new_bill=True))
    # 生产订单生成单据
    #print(mo_create())
    # 复制产生新的生产订单
    # print(mo_copy())
     # print(mo_copy(FBillNo='MO033530'))
    # MO033531
    #print([None,None,None])
    #单据类型处理
    # print(mo_billType_getNumber())
    # print(mo_billType_getNumber('直接入库-普通生产'))
    # print(mo_billTypeList())
    #print(mo_copy(FBillNo='MO033541'))
   # print(mo_reSave(FBillNo='MO033561'))
   #print(str(datetime.datetime.now()) +'系统自动更新')
    #print(mo_actionTime())
    #mydata = ['MO033566','MO033567']
    #mo_reSave_batch(FBillNoList = mydata)
    #查询待处理的生产订单
    # print(mo_list_newToDo())
    mydata = mo_list_newToDo()
    # print(mydata)
    #mo_reSave_batch(FBillNoList = mydata,FBillType=mo_billType_stockIn_common())
    #print(len(null))
    #print(stockPlace_tpl())
    # print(mo_billTypeList())
    # print(mo_billType_stockIn_common())
    # print(mo_testData_keys())
    # print(type(mo_testData_keys()))
    # print(mo_reSave_auto())