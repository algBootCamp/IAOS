# IAOS(Intelligent analysis of securities)证券智能分析系统
### 主要功能:

#### 1. 量化选股
- 多因子选股
- 趋势跟踪选股


#### 2. 量化择时


#### 3. 条件选股
- 选股范围：市场【沪深】、行业
- 基本面：
  1. 估值指标【市盈率、市净率、总股本、总市值、流通股本、流通市值】
  2. 财务指标【净利润、净利润增长率、营业收入、毛利率、净利率、每股现金流、每股收益、每股净资产、资产负债率、股东户数、股息率、净资产收益率、营收增长率】
- 技术面：股价、涨跌幅、涨跌停、换手率、振幅、成交量量比、主力资金、委比、成交额
- 按照选定的上述条件取交集


#### 4. 个股量化分析
- 个股量化的初步想法：给出以下几个方面的分析结果：基本面分析、趋势分析、筹码分析、一致预期分析【如有数据】

#### 5. 行业分类、周期非周期股分类、大、中小盘股分类


#### 6. 侦测大盘周期、情绪

---
### 初步设想的一个闭环逻辑：
- 模式一：\
1- 侦测大盘周期与情绪 \
2- 基于1选择合适的选股策略模型 \
3- 基于2得出的股票池，进行个股的量化分析 【结果大致是：进场 观望 （可分等级）】 \
4- 基于3的结果，对个股进行量化择时【需要实时行情】，给出买卖时机 买卖价格 \
- 模式二： \
1- 条件选股 \
2- 基于1，进行个股量化分析【结果大致是：进场 观望 （可分等级）】 \
3- 基于2的结果，对个股进行量化择时【需要实时行情】，给出买卖时机 买卖价格

----

### 后端功能模块说明
- #### app.py：应用入口
- #### conf：配置模块
- #### web.controller：web接口模块
- #### web.service：web逻辑模块
- #### quotation.captures：行情数据获取
- #### quotation.cleaning：行情数据清洗模块
- #### quotation.cache：基础数据缓存
- #### entity：实体类
- #### db：持久层组件、dolphindb接口、redis、脚本模块
- #### scheduledtask：定时任务
- #### quantization.securitypick：量化选证券/股模块
- #### quantization.strategy：策略模块
- #### quantization.timing：量化择时
- #### quantization.factors：因子
- #### quantization.backtest：回测模块
- #### util：通用工具
- #### test：测试
- #### docs：参考文档、功能介绍文档等
- #### static：web前端静态文件
- #### templates：web前端模版文件

--- 
### 参考资料
- [量化策略系列文章](https://blog.csdn.net/weixin_35757704/category_12162608.html)
- [akshare](https://gitcode.net/mirrors/akfamily/akshare/-/tree/master/docs)
- [akshare doc](https://www.akshare.xyz/demo.html)
- [研报复现01](https://blog.csdn.net/weixin_43915798/category_10971751.html)
- [研报复现02](https://blog.csdn.net/weixin_42219751/category_9059115.html)
- [tushare](https://www.tushare.pro/)
- [waditu研报](https://waditu.com/#/search/report)
- [waditu doc](https://github.com/waditu)
- [CZSC](https://s0cqcxuy3p.feishu.cn/wiki/wikcnNgfYsvULhW8SC5rd1t97Pb?create_from=create_doc_to_wiki)
- [vnpy](https://github.com/vnpy/vnpy)
