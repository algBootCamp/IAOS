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


#### 5. 行业分类、周期非周期股分类、大、中小盘股分类


#### 6. 侦测大盘周期

---

## 后端功能模块说明
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

