from k3cloud_webapi_sdk.main import K3CloudApiSdk
import json
# 客户按编码进行查看
def customer_view(config_path='E:\data\data\github\conf.ini',kdc_url='http://47.103.221.12:8126/k3cloud',FNumber="01.01.01.0001"):
    api_sdk = K3CloudApiSdk(kdc_url)
    api_sdk.Init(config_path=config_path, config_node='config')
    data = {"CreateOrgId": 0,"Number": FNumber}
    r = api_sdk.View(formid='BD_Customer',data=data)
    data = json.loads(r)
    # print(data)
    if data["Result"]["ResponseStatus"] is None:
        # print(data["Result"]["ResponseStatus"] is None)
        FId = data["Result"]["Result"]["Id"]
        FDocumentStatus = data["Result"]["Result"]["DocumentStatus"]
        FName = data["Result"]["Result"]["Name"][0]["Value"]
        FCreateOrgId = data["Result"]["Result"]["CreateOrgId"]["Id"]
        FCreateOrgName = data["Result"]["Result"]["CreateOrgId"]["Name"][0]["Value"]
        FCreateOrgNumber = data["Result"]["Result"]["CreateOrgId"]["Number"]
        FUseOrgId = data["Result"]["Result"]["UseOrgId"]["Id"]
        FUseOrgName = data["Result"]["Result"]["UseOrgId"]["Name"][0]["Value"]
        FUseOrgNumber = data["Result"]["Result"]["UseOrgId"]["Number"]
        FCreatorId = data["Result"]["Result"]["CreatorId"]["Id"]
        FCreatorName = data["Result"]["Result"]["CreatorId"]["Name"]
        FModifierId = data["Result"]["Result"]["ModifierId"]["Id"]
        FModifierName = data["Result"]["Result"]["ModifierId"]["Name"]
        FCreateDate = data["Result"]["Result"]["CreateDate"]
        FModifyDate = data["Result"]["Result"]["FModifyDate"]
        FTel = data["Result"]["Result"]["TEL"]
        FTaxRegisterCode = data["Result"]["Result"]["FTAXREGISTERCODE"]
        FTradingCurrId = data["Result"]["Result"]["TRADINGCURRID"]["Id"]
        FTradingCurrName = data["Result"]["Result"]["TRADINGCURRID"]["Name"][0]["Value"]
        FTradingCurrNumber = data["Result"]["Result"]["TRADINGCURRID"]["Number"]
        FRecConditionId = data["Result"]["Result"]["RECCONDITIONID"]["Id"]
        FRecConditionName = data["Result"]["Result"]["RECCONDITIONID"]["Name"][0]["Value"]
        FRecConditionNumber = data["Result"]["Result"]["RECCONDITIONID"]["Number"]
        FIsCreditCheck = data["Result"]["Result"]["FISCREDITCHECK"]
        FApproverId = data["Result"]["Result"]["APPROVERID"]['Id']
        FApproverName = data["Result"]["Result"]["APPROVERID"]['Name']
        FApproveDate = data["Result"]["Result"]["APPROVEDATE"]
        FForbidderId = data["Result"]["Result"]["FORBIDDERID"]
        FForbidDate = data["Result"]["Result"]["FORBIDDATE"]
        FTaxTypeId = data["Result"]["Result"]["TaxType"]["Id"]
        FTaxTypeNumber = data["Result"]["Result"]["TaxType"]["FNumber"]
        FTaxTypeName = data["Result"]["Result"]["TaxType"]["FDataValue"][0]["Value"]
        FCustTypeId = data["Result"]["Result"]["CustTypeId"]["Id"]
        FCustTypeNumber = data["Result"]["Result"]["CustTypeId"]["FNumber"]
        FCustTypeName = data["Result"]["Result"]["CustTypeId"]["FDataValue"][0]["Value"]
        FAddress = data["Result"]["Result"]["ADDRESS"]
        FWebsite = data["Result"]["Result"]["WEBSITE"]
        FGroupId = data["Result"]["Result"]["FGroup"]["Id"]
        FGroupNumber = data["Result"]["Result"]["FGroup"]["Number"]
        FGroupName = data["Result"]["Result"]["FGroup"]["Name"][0]["Value"]
        FInvoiceType = data["Result"]["Result"]["InvoiceType"]
        FTaxRateId = data["Result"]["Result"]["TaxRate"]["Id"]
        FTaxRateNumber = data["Result"]["Result"]["TaxRate"]["Number"]
        FTaxRateName = data["Result"]["Result"]["TaxRate"]["Name"][0]["Value"]
        FIsGroup = data["Result"]["Result"]["IsGroup"]
        FIsTrade = data["Result"]["Result"]["IsTrade"]
        FInvoiceTitle = data["Result"]["Result"]["INVOICETITLE"]
        FInvoiceBankName = data["Result"]["Result"]["INVOICEBANKNAME"]
        FInvoiceBankAccount = data["Result"]["Result"]["INVOICEBANKACCOUNT"]
        FInvoiceTel = data["Result"]["Result"]["INVOICETEL"]
        FInvoiceAddress = data["Result"]["Result"]["INVOICEADDRESS"]
        # print(type(data))
        res = {}
        res["FId"] = FId
        res["FNumber"] = FNumber
        res['FName'] = FName
        res["FCreateOrgId"] = FCreateOrgId
        res["FCreateOrgName"] = FCreateOrgName
        res["FCreateOrgNumber"] = FCreateOrgNumber
        res["FDocumentStatus"] = FDocumentStatus
        res["FUseOrgId"] = FUseOrgId
        res["FUseOrgName"] = FUseOrgName
        res["FUseOrgNumber"] = FUseOrgNumber
        res["FCreatorId"] = FCreatorId
        res["FCreatorName"] = FCreatorName
        res["FModifierId"] = FModifierId
        res["FModifierName"] = FModifierName
        res["FCreateDate"] = FCreateDate
        res["FModifyDate"] = FModifyDate
        res["FTel"] = FTel
        res["FTaxRegisterCode"] = FTaxRegisterCode
        res["FTradingCurrId"] = FTradingCurrId
        res["FTradingCurrName"] = FTradingCurrName
        res["FTradingCurrNumber"] = FTradingCurrNumber
        res["FRecConditionId"] = FRecConditionId
        res["FRecConditionName"] = FRecConditionName
        res["FRecConditionNumber"] = FRecConditionNumber
        res["FIsCreditCheck"] = FIsCreditCheck
        res["FApproverId"] = FApproverId
        res["FApproverName"] = FApproverName
        res["FApproveDate"] = FApproveDate
        res["FForbidderId"] = FForbidderId
        res["FForbidDate"] = FForbidDate
        res["FTaxTypeId"] = FTaxTypeId
        res["FTaxTypeNumber"] = FTaxTypeNumber
        res["FTaxTypeName"] = FTaxTypeName
        res["FCustTypeId"] = FCustTypeId
        res["FCustTypeNumber"] = FCustTypeNumber
        res["FCustTypeName"] = FCustTypeName
        res["FAddress"] = FAddress
        res["FWebsite"] = FWebsite
        res["FGroupId"] = FGroupId
        res["FGroupNumber"] = FGroupNumber
        res["FGroupName"] = FGroupName
        res["FInvoiceType"] = FInvoiceType
        res["FTaxRateId"] = FTaxRateId
        res["FTaxRateNumber"] = FTaxRateNumber
        res["FTaxRateName"] = FTaxRateName
        res["FIsGroup"] = FIsGroup
        res["FIsTrade"] = FIsTrade
        res["FInvoiceTitle"] = FInvoiceTitle
        res["FInvoiceBankName"] = FInvoiceBankName
        res["FInvoiceBankAccount"] = FInvoiceBankAccount
        res["FInvoiceTel"] = FInvoiceTel
    else:
        res = None

    return (res)

if __name__ == '__main__':
    print(customer_view(FNumber='01.01.01.0015'))
