#!/usr/bin/python
# -*- coding:UTF-8 -*-
from k3cloud_webapi_sdk.main import K3CloudApiSdk
import time
import json
# 首先构造一个SDK实例
api_sdk = K3CloudApiSdk('http://47.103.221.12:8126/k3cloud')
# 然后初始化SDK，需指定如下配置文件相关参数，否则会导致SDK初始化失败而无法使用：
# config_path:配置文件的相对或绝对路径，建议使用绝对路径
# config_node:配置文件中的节点名称
api_sdk.Init(config_path='../cfg/conf.ini', config_node='config')
# 比如查询“物料”(BD_MATERIAL)单据中的“物料名称”(FName)字段
# 单据查询
# print(api_sdk.ExecuteBillQuery({"FormId": "BD_MATERIAL", "FieldKeys": "FNumber,FName"}))

# 生产订单查看

data_mo_src = api_sdk.View("PRD_MO", {
    "CreateOrgId": 0,
    "Number": "MO033489",
    "Id": ""
})
print(data_mo_src)
#将文本转化为对象
data_mo_src =  json.loads(data_mo_src)
mo_bill_src = data_mo_src['Result']['Result']
# 单据内码 取值或者手工处理
FId_src = mo_bill_src['Id']
# FId_src = 0
#print(FId_src)
# 单据日期
# 2020-10-02T00:00:00
# 2020-10-02
FDate_src = mo_bill_src['Date']
# sprint(FDate_src)
# 生产组织
FPrdOrgId_number_src = mo_bill_src['PrdOrgId']['Number']
# print(FPrdOrgId_number_src)
# '100.01'
#表头备注
if len(mo_bill_src['Description']) > 0:
    FDescription_src = mo_bill_src['Description'][0]['Value']
else:
    FDescription_src = ''


# PPBOM00035794
# PPBOM00035795

FDescription_src = 'cdf'
print(FDescription_src)
#出货安排
F_NLJ_delivery_src = mo_bill_src['F_NLJ_delivery']
#出口单据批号带入
F_NLJ_calcBatch_src = mo_bill_src['F_NLJ_calcBatch']
#F_NLJ_calcBatch_src = True
print(F_NLJ_calcBatch_src )
#国内订单批号带入
F_NLJ_insideID_src = mo_bill_src['F_NLJ_insideID']
#print(F_NLJ_insideID_src)
#----------------------------------------
#---------以下为产品明细
#产品类型
FProductType_src = mo_bill_src['TreeEntity'][0]['ProductType']
#print(mo_bill_src['TreeEntity'][0]['ProductType'])
# '1'
#物料
FMaterialId_Number_src = mo_bill_src['TreeEntity'][0]['MaterialId']['Number']
#print(FMaterialId_Number_src)
#单位
FUnitId_Number_src = mo_bill_src['TreeEntity'][0]['UnitId']['Number']
#print(FUnitId_Number_src)
# 0601
# 计划生产数量
FQty_src = mo_bill_src['TreeEntity'][0]['Qty']
# print(FQty_src)
#生产车间
FWorkShopID_src = mo_bill_src['TreeEntity'][0]['WorkShopID']['Number']
#print(FWorkShopID_src)
# '19.04'
#需求组织
FRequestOrgId_Number_src = mo_bill_src['TreeEntity'][0]['RequestOrgId']['Number']
print(FRequestOrgId_Number_src)
#bom版本
FBomId_src = mo_bill_src['TreeEntity'][0]['BomId']['Number']
print(FBomId_src)
# 是否倒冲，默认为false
FISBACKFLUSH_src = mo_bill_src['TreeEntity'][0]['ISBACKFLUSH']
print(FISBACKFLUSH_src)
# 入库组织
FStockInOrgId_src = mo_bill_src['TreeEntity'][0]['StockInOrgId']['Number']
print(FStockInOrgId_src)
# '100.01'
# 基础生产数量
FBaseYieldQty_src = mo_bill_src['TreeEntity'][0]['BaseYieldQty']
print(FBaseYieldQty_src)


# 72.0
# 入库上限
FBaseStockInLimitH_src = mo_bill_src['TreeEntity'][0]['BaseStockInLimitH']
print(FBaseStockInLimitH_src)
#入库下限
FBaseStockInLimitL_src = mo_bill_src['TreeEntity'][0]['BaseStockInLimitL']
print(FBaseStockInLimitL_src)

#基础单位数量
FBaseUnitQty_src = mo_bill_src['TreeEntity'][0]['BaseUnitQty']
print(FBaseUnitQty_src)
#基本单位
FBaseUnitId_Number_src = mo_bill_src['TreeEntity'][0]['BaseUnitId']['Number']
print(FBaseUnitId_Number_src)
#产品默认入库仓库
FStockId_Number_src = mo_bill_src['TreeEntity'][0]['StockId']['Number']
print(FStockId_Number_src)
# 产品仓位的设置
FStockLocId_src = mo_bill_src['TreeEntity'][0]['StockLocId']
# print(FStockLocId_src)
data_StockPlace_tpl = {
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
#针对仓位集进行设置
if FStockLocId_src['F100001_Id'] > 0 :
    data_StockPlace_tpl['FSTOCKLOCID__FF100001']['FNumber'] = FStockLocId_src['F100001']['Number']

if FStockLocId_src['F100004_Id'] > 0 :
    data_StockPlace_tpl['FSTOCKLOCID__FF100004']['FNumber'] = FStockLocId_src['F100004']['Number']

if FStockLocId_src['F100005_Id'] > 0 :
    data_StockPlace_tpl['FSTOCKLOCID__FF100005']['FNumber'] = FStockLocId_src['F100005']['Number']

if FStockLocId_src['F100006_Id'] > 0 :
    data_StockPlace_tpl['FSTOCKLOCID__FF100006']['FNumber'] = FStockLocId_src['F100006']['Number']

if FStockLocId_src['F100007_Id'] > 0 :
    data_StockPlace_tpl['FSTOCKLOCID__FF100007']['FNumber'] = FStockLocId_src['F100007']['Number']

if FStockLocId_src['F100008_Id'] > 0 :
    data_StockPlace_tpl['FSTOCKLOCID__FF100008']['FNumber'] = FStockLocId_src['F100008']['Number']

if FStockLocId_src['F100009_Id'] > 0 :
    data_StockPlace_tpl['FSTOCKLOCID__FF100009']['FNumber'] = FStockLocId_src['F100009']['Number']

if FStockLocId_src['F100010_Id'] > 0 :
    data_StockPlace_tpl['FSTOCKLOCID__FF100010']['FNumber'] = FStockLocId_src['F100010']['Number']

if FStockLocId_src['F100012_Id'] > 0 :
    data_StockPlace_tpl['FSTOCKLOCID__FF100012']['FNumber'] = FStockLocId_src['F100012']['Number']



#print(data_StockPlace_tpl)

#入库上限
FStockInLimitH_src = mo_bill_src['TreeEntity'][0]['StockInLimitH']
print(FStockInLimitH_src)
#入库下限
FStockInLimitL_src = mo_bill_src['TreeEntity'][0]['StockInLimitL']
print(FStockInLimitL_src)
#未入库数量
FNoStockInQty_src = mo_bill_src['TreeEntity'][0]['NoStockInQty']
print(FNoStockInQty_src)
#未入库数量
FBaseNoStockInQty_src = mo_bill_src['TreeEntity'][0]['BaseNoStockInQty']
print(FBaseNoStockInQty_src)



# 生产订单按列表进行查看
# print(api_sdk.ExecuteBillQuery({"FormId": "PRD_MO", "FieldKeys": "FBillNo,FDate" ,"FilterString": "FBillNo like 'MO03345%'", "TopRowCount": 100}))


# 生产订单数据的保存
#单据类型
#   直接入库 SCDD03_SYS
#   汇报入库 SCDD01_SYS
#   "FID": 取值如下
#   如果为0表示创建单据
#   如果为已经ID表示修改单据
mo_data = {
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
        "FID": FId_src,
        "FBillType": {
            "FNUMBER": "SCDD01_SYS"
        },
        "FDate": FDate_src,
        "FPrdOrgId": {
            "FNumber": FPrdOrgId_number_src
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
        "FDescription": FDescription_src,
        "FIsEntrust": "false",
        "FEnTrustOrgId": {
            "FNumber": ""
        },
        "FPPBOMType": "1",
        "FIssueMtrl": "false",
        "F_NLJ_Text": "",
        "F_NLJ_ActualDate": FDate_src,
        "F_NLJ_calcBatch": F_NLJ_calcBatch_src,
        "F_NLJ_RDStatus": "",
        "F_NLJ_insideID": F_NLJ_insideID_src,
        "F_NLJ_delivery": F_NLJ_delivery_src,
        "FTreeEntity": [
            {
                "FEntryId": 0,
                "FProductType": FProductType_src,
                "FMaterialId": {
                    "FNumber": FMaterialId_Number_src
                },
                "FUnitId": {
                    "FNumber": FUnitId_Number_src
                },
                "FQty": FQty_src,
                "FYieldQty": 0,
                "FWorkShopID": {
                    "FNumber": FWorkShopID_src
                },
                "FPlanStartDate": FDate_src,
                "FPlanFinishDate": FDate_src,
                "FRequestOrgId": {
                    "FNumber": FRequestOrgId_Number_src
                },
                "FBomId": {
                    "FNumber": FBomId_src
                },
                "FISBACKFLUSH": FISBACKFLUSH_src,
                "FLot": {
                    "FNumber": ""
                },
                "FStockInOrgId": {
                    "FNumber": FStockInOrgId_src
                },
                "FBaseYieldQty": FBaseYieldQty_src,
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
                "FBaseStockInLimitH":FBaseStockInLimitH_src,
                "FInStockOwnerId": {
                    "FNumber": ""
                },
                "FInStockType": "",
                "FStockInLlRatio": 0.0,
                "FCheckProduct": "false",
                "FOutPutOptQueue": "",
                "FBaseStockInLimitL": FBaseStockInLimitL_src,
                "FBaseUnitQty": FBaseUnitQty_src,
                "FRepQuaSelAuxQty": 0,
                "FRepQuaAuxQty": 0,
                "FRepFailSelAuxQty": 0.0,
                "FStockInReMadeSelQty":0.0,
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
                    "FNumber": FBaseUnitId_Number_src
                },
                "FStockInFailSelQty": 0.0,
                "FStockId": {
                    "FNumber": FStockId_Number_src
                },
                "FStockInFailQty": 0.0,
                "FRepQuaSelQty": 0.0,
                "FStockLocId": data_StockPlace_tpl,
                "FRepQuaQty": 0.0,
                "FStockInLimitH": FStockInLimitH_src,
                "FRepFailSelQty": 0.0,
                "FRepFailQty": 0.0,
                "FStockInLimitL": FBaseStockInLimitL_src,
                "FOperId": 0,
                "FProcessId": {
                    "FNumber": ""
                },
                "FCostRate": 100.000000,
                "FCreateType": "1",
                "FYieldRate": 100.0000000000,
                "FGroup": 1,
                "FNoStockInQty": FNoStockInQty_src,
                "FParentRowId": "",
                "FRowExpandType": 0,
                "FBaseNoStockInQty": FBaseNoStockInQty_src,
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
                "F_NLJ_SONote": "",
                "F_NLJ_SOBodyNote": "",
                "FCloseReason": "",
                "F_NLJ_SOBODYNOTE2": "",
                "F_NLJ_BatchNote": "",
                "FIsFirstInspect": "false",
                "F_NLJ_LastPickDate": "1900-01-01",
                "FFirstInspectStatus": "",
                "F_NLJ_PrdStockDate": "1900-01-01",
                "F_NLJ_UnPickInfo": "",
                "F_NLJ_FirstDate": "1900-01-01",
                "F_NLJ_DirectPickFlag": "false",
                "F_NLJ_Combo": "",
                "F_NLJ_LableItemModel": "",
                "F_NLJ_LableItemModel_KWSJ": "",
                "F_NLJ_PrdColor": "",
                "F_NLJ_Additive": "",
                "F_NLJ_BloodCollectionVol": "",
                "F_NLJ_CollectionVol": "",
                "F_NLJ_Reagent": "",
                "F_NLJ_TubeModel": "",
                "F_NLJ_TubeMaterial": "",
                "F_NLJ_QtyShowText": "",
                "F_NLJ_PkgQty": "",
                "F_NLJ_ApplyAltitude": "",
                "F_NLJ_SterilizationMethod": "",
                "F_NLJ_LabelNote1": "",
                "F_NLJ_SpecialOR": "",
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
        ],
        "FScheduledEntity": [
            {
                "FEntryID": 0
            }
        ]
    }
}

#print(mo_data)

#print(api_sdk.Save("PRD_MO", mo_data))

# 生产订单提交
data_mo_submit = {
    "CreateOrgId": 0,
    "Numbers": ['MO033473'],
    "Ids": "",
    "SelectedPostId": 0,
    "NetworkCtrl": ""
}

# print(api_sdk.Submit('PRD_MO',data_mo_submit))

# 生产订单审核
data_mo_audit = {
    "CreateOrgId": 0,
    "Numbers": ['MO033473'],
    "Ids": "",
    "InterationFlags": "",
    "NetworkCtrl": ""
}

# print(api_sdk.Audit('PRD_MO',data_mo_audit))

#生产订单反审核
data_mo_UnAudit ={
    "CreateOrgId": 0,
    "Numbers": ['MO033473'],
    "Ids": "",
    "InterationFlags": "",
    "NetworkCtrl": ""
}
# print(api_sdk.UnAudit('PRD_MO',data_mo_UnAudit))

#生产订单删除接口
data_mo_del = {
    "CreateOrgId": 0,
    "Numbers": ['MO033473'],
    "Ids": "",
    "NetworkCtrl": ""
}
# print(api_sdk.Delete('PRD_MO',data_mo_del))

#生产订单执行接口，执行至下达
#在执行生产订单下达之前，需要检查一下对应的生产用料清单是否已审核
data_mo_toRelease = {
    "CreateOrgId": 0,
    "Numbers": ['MO033489'],
    "Ids": "",
    "NetworkCtrl": ""
}
print(api_sdk.ExcuteOperation("PRD_MO","ToRelease",data_mo_toRelease))
