

def user_agent_parse(param_str):
    def containswith(search_text_list):
        for search_text in search_text_list:
            if search_text in param_str:
                return True
        return False
    ret = ''
    if containswith(['Mobile']):
        ret += 'Mobile '
    else:
        ret += 'PC '

    map_list = [
        (["iPhone"], "苹果"),
        (["MicroMessenger"], "微信"),
        (["AlipayClient"], "支付宝"),

        (["QQTheme"], "QQ"),



        (["QQBrowser"], "QQ浏览器"),
        (["baiduboxapp", "baidu"], "百度"),
        (["Weibo"], "Weibo"),
        (["iqiyi"], "爱奇艺"),
        (["aweme"], "抖音"),
        (["kdtUnion_iting"], "喜马拉雅"),
        (["DingTalk"], "钉钉"),
        (["UCBrowser"], "UC"),
        (["SamsungBrowser"], "三星"),
        (["Sogou"], "搜狗"),
        #### 这里开始放手机手机型号
        (["HONORHRY"], "荣耀"),
        (["NokiaBrowser"], "诺基亚"),

        (["VivoBrowser", "vivo", "V1818T"], "Vivo"),
        (["HeyTapBrowser"], "HeyTap"),
        (["PCHM30", "OppoBrowser", "PDPM00", "PBEM00"], "OPPO"),
        (["HUAWEIEVA", "HuaweiBrowser", "huaweioem", "HUAWEI", "HWI-AL00", "HUAWEIELE", "INE-AL00", "LDN-AL00", "TAS-AN00"], "华为"),
        (["XiaoMi", "MiuiBrowser"], "小米"),
        (["HD1910"], "OnePlus"),
        (["MZBrowser"], "魅族"),
        (["Opera", "PDPM00", "PBEM00"], "Opera"),
        (["Chrome"], "谷歌"),
        (["Safari", "iPhone"], "苹果"),

    ]

    has_searched = False
    for contain_list, keyword in map_list:
        if containswith(contain_list):
            ret += keyword
            break

    if not has_searched:
        ret += "其他"

    return ret
