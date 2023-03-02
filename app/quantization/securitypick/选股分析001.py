
# coding: utf-8
#请关注微信 公众号：Python金融量化
#原创不易，引用请注明出处，如果觉得对你有帮助，请赞赏或点赞，谢谢！

# ### 前言
# 
# 《【Python金融量化】上市公司知多少？》一文对A股上市公司的基本概况做了一个简要的可视化分析，延续那篇文章，
# 本文将继续介绍基于tushare获取数据，使用python进行数据清洗、特征分组和排序，一步步筛选出符合设定条件的股票组合。
# 
# #### 指导逻辑
# 
# 选股涉及两个方面，一是公司分析，包括财务状况、发展潜力和成长性等，这方面是俗称的基本面分析，可以参考的资料已经汗牛充栋；二是股票分析。
# 股票分析主要回答三个问题：  
# （1）如何判断一只股票有投资价值？  
# （2）如何从股票池中选出符合自己认为有价值的股票？  
# （3）选出合适的股票后如何构建投资组合并动态调整？  
# 
# 总体思维：多层次多角度分析  
# 多角度保证在市场大方向上看对的正确率尽可能增加，多层次可以和多角度相互验证，获取超额收益。  
# 通过自上而下的分析框架确定投资方向，选择符合投资方向的最优标的。  
# 
# 操作思路：根据股票基本面指标进行排序，通过设置参数和过滤值筛选投资标的，
# 具体指标包括市盈率、市净率、流通股本、总市值、每股公积金、每股收益、收入同比、利润同比、毛利率、净利润率等。
# 
# 
# #### 敬告
# 本文不详细展开对股市投资逻辑和选股策略的理解，主要介绍基于python如何一步步筛选出符合自己设定要求的股票组合，希望能起到抛砖引玉的作用。
# 文中提及股票和选股思路不构成投资建议或交易策略。交易有风险，入市需谨慎！

# ### 前期准备
# #### 导入需要的包

# In[121]:


#先引入后面可能用到的包（package）
import pandas as pd  
import numpy as np
from scipy import stats
import tushare as ts 
import matplotlib.pyplot as plt
# get_ipython().run_line_magic('matplotlib', 'inline')

#正常显示画图时出现的中文和负号
from pylab import mpl
mpl.rcParams['font.sans-serif']=['SimHei']
mpl.rcParams['axes.unicode_minus']=False


# #### 数据获取
# 基于tushare开源包获取A股基本面和交易数据。

# In[122]:


#基本面数据
basics_data=ts.get_stock_basics()
#时间默认为当前交易日的上一个交易日
#交易数据
trade_data=ts.get_today_all()
#时间默认为当前交易日的上一个交易日


# In[123]:


#了解数据1
basics_data.head(3)


# 各变量名称含义：code,代码；
# name,名称；
# industry,细分行业；
# area,地区；
# pe,市盈率；
# outstanding,流通股本；
# totals,总股本(万)；
# totalAssets,总资产(万)；
# liquidAssets,流动资产；
# fixedAssets,固定资产；
# reserved,公积金；
# reservedPerShare,每股公积金；
# eps,每股收益；
# bvps,每股净资；
# pb,市净率；
# timeToMarket,上市日期；
# undp 未分配利润；
# perundp 每股未分配；
# rev 收入同比（%）；
# profit 利润同比（%）；
# gpr 毛利率（%）；
# npr 净利润率（%）；
# holders_num 股东人数

# In[124]:


#了解数据2
trade_data.head(3)


# 各变量含义：
# 代码，名称，涨跌幅，现价，开盘价，最高价，
# 最低价，昨日收盘价，成交量，换手率，成交额，市盈率，市净率，总市值，流通市值

# #### 数据清洗
# 数据清洗过程大致包含：选择子集、列名重命名、缺失数据处理、数据类型转换、数据排序、异常值处理等。

# In[125]:


#选择子集和为变量重命名
#基本面数据包含的变量22列，交易数据15列，只保留后面分析要用到的几个指标
#保留code、name、流通股本、市盈率、市净率、每股收益
#每股公积、收入同比、利润同比、毛利率、净利率
#流通市值、收盘价、总市值

#基本面数据清洗
col=['name','outstanding','pe','pb','esp',
     'reservedPerShare','rev','profit','gpr','npr']
newcol=['简称','流通股','市盈率','市净率','每股收益','每股公积',
        '收入同比','利润同比','毛利率','净利率']
d=dict(zip(col,newcol))
b_data=basics_data.loc[:,col]
b_data.rename(columns=d,inplace=True)
b_data.head()


# In[126]:


#交易数据清洗
##当前股价,如果停牌则设置当前价格为上一个交易日股价 
trade_data['trade'] = trade_data.apply(lambda x:x.settlement if x.trade==0 else x.trade, axis=1) 
#选取股票代码,名称,当前价格,总市值,流通市值 
t_data = trade_data.loc[:,['code', 'trade', 'mktcap', 'nmc','volume','turnoverratio']] 
#设置行情数据code为index列 
t_data = t_data.set_index('code') 
t_data.rename(columns={'trade':'收盘价','mktcap':'总市值','nmc':'流通市值',
                       'volume':'成交量','turnoverratio':'换手率'},inplace=True)
#将总市值和流通值换成亿元单位
t_data['总市值'] = t_data['总市值'] / 10000 
t_data['流通市值'] = t_data['流通市值'] / 10000 
t_data.head(3)


# In[127]:


#合并两个数据表 
data = b_data.merge(t_data, left_index=True, right_index=True) 
data.head(3)


# In[128]:


#数据描述性统计
data.describe().round(2)


# ### 数据探索与分析
# 

# #### 大盘股vs小盘股
# 小盘股是相对大盘股而言的，而中盘股是介于大盘股和小盘股之间。市场上传统划分方法是根据流通股本的大小：一般流通股本超过10亿股为大盘股，流通股本小于5亿股为小盘股，流通股本5亿-10亿的属于中盘股。如果以市值衡量，总市值大于1000亿的属于超大盘股，总市值大于500亿以上的属于大盘股，总市值小于200亿的属于小盘股，处于200亿-500亿总市值的股票，属于中盘股。
#   
# 实际上关于大盘股和中小盘股的划分并没有统一的标准。大盘股和小盘股的区别并不是固定的，随着上市公司的增多，以及A股市场总市值的不断变化，大小盘的划分标准也应该是动态变化的。
# 
# 为什么要划分大盘股和中小盘股呢？换句话，大盘股和小盘股有什么明显的区别吗？一般而言，相同业绩的个股，小盘股的市盈率比中盘股高，中盘股要比大盘股高。特别在市场疲软时，小盘股机会较多。在牛市时大盘股和中盘股较适合大资金的进出，因此盘子大的个股比较看好。由于流通盘大，对指数影响大，往往成为市场调控指数的工具。投资者选择个股，一般熊市应选小盘股和中小盘股，牛市应选大盘股和中大盘股。  
# In[129]:


#生成频率表
#利用cut函数，将连续变量转为分类变量
def df_cut(data, cut, labels=None): 
    min_num = data.min() 
    max_num = data.max() 
    b = [min_num] + cut + [max_num]
    if not labels: 
        labels = range(len(cut)+1)
    else: 
         labels=[labels[i] for i in range(len(cut)+1)] 
    Bin = pd.cut(data,bins=b,
         labels=labels,include_lowest=True)    
    return Bin 

#data['流通股'].quantile(0.9)
#由于流通股的90分位数点为20亿左右，中位数为5亿左右
#这里将流通股本小于5亿的划分为小盘股，大于20亿的为大盘股
#当然也可以使用总市值来划分，或者使用流通股本和收盘价中位数来确定

cut = [5,20] 
labels=['小盘股', '中盘股','大盘股'] 
#调用函数df_cut,增加新列
data_new=data.loc[:,['简称','收盘价','流通股','市盈率','每股收益','净利率','收入同比','利润同比']]
data_new['股票类型'] = df_cut(data['流通股'], cut, labels) 
#查看标签列，取值范围前面加上了序号，是便于后面生成表格时按顺序排列
data_new.head()


# In[130]:


data_new.groupby('股票类型')[['市盈率','收盘价','每股收益']].describe(percentiles=[0.5]).round(2)


# 从分组描述性统计上看，小盘股市盈率平均值明显高于大盘股，高达75倍；小盘股股价平均值为15.47元，是大盘股股价平均值的两倍左右。可见二者在估值上还是存在较大差异的。如果要从更严谨的角度去判别，可以根据分组统计结果对数据进行统计上的T检验，这里不再展开分析。

# In[131]:


data_new.groupby('股票类型')[['净利率','利润同比','收入同比']].describe(percentiles=[]).round(2)


# 从净利率上看，大盘股明显占优，平均12.64%的净利率，而中盘股是-11.56%，看来今年营商环境恶劣，承压比较大的是中盘股类型的上市公司。大盘股往往是传统行业，例如银行、房地产、钢铁、石油石化、煤炭、有色金属等，还是最赚钱的主啊。此外，可以发现一个有趣的现象，中小盘股内部两级分化很严重，如小盘股净利率最高的达1332.62%，最差的为-14735.66%，意味着有的中小盘股逆势赚钱，有的可能已经亏到“底裤”都没了。收入同比上，是小盘股占优，一般而言，中小盘股的成长性要比大盘股好，但是波动性也明显更大。关于规模与股票估值可以深入挖掘的东西还很多，特别是可以使用分位数回归，研究不同规模股票之间的收益率差异。

# #### 毛利率
# 计算公式：毛利率=（销售收入－销售成本）/销售收入×100%。毛利率对于判断公司盈利能力而言是很重要的指标，高毛利可以反映出公司的竞争优势。但是不同行业间毛利差异是很大的，一般要在同一个行业里比较。一般而言，毛利率越高反映公司盈利能力越强，公司投资价值越高。但是，要注意不能单纯使用该指标来选股，因为高毛利背后也有坑，如把成本算到费用去了（如某些软件公司），毛利率自然就高，一定要结合净利率来看。

# In[132]:


#根据毛利率高低排序，选出毛利率最高的十只股票。


# In[133]:


data.sort_values('毛利率',ascending=False)[:10]


# 以上十只股票的毛利率都超过90%，但是净利率并不高！第十只股票山东金泰出现了亮点：毛利率94.36%，但是净利率却是-177.2%，利润同比-58.91%，可以说是very interesting了，感兴趣的朋友可以深入挖掘下，这年头陷阱太多，单一角度看问题，很容易掉坑里（是我太单纯，还是世界太复杂！）。从山东金泰近两年走势来看，相对大盘指数跌了很多，可见市场还是相对“理性”的。

# In[134]:


#构建股票数据获取和可视化函数
def get_data_plot(code,startdate,name):
    sh=ts.get_k_data('sh',start=startdate)
    sh.index=pd.to_datetime(sh.date)
    df=ts.get_k_data(code,start=startdate)
    df.index=pd.to_datetime(df.date)
    fig = plt.figure(figsize=(12,6))  
    ax1 = fig.add_subplot(111)  
    ax1.plot(df['close'],color='r',label=name)
    ax1.legend(loc=2)
    ax2=ax1.twinx()
    ax2.plot(sh['close'],color='k',label='上证指数')
    plt.title(name+'vs上证指数近几年走势',fontsize=15)
    ax2.legend(loc=1)
    plt.show()


# In[135]:


get_data_plot('600385','2017-01-01','山东金泰')


# In[136]:


#再来看看毛利率最低的十只股票
data.sort_values('毛利率',ascending=True)[:10]


# In[137]:


m=data[data['毛利率']<0]['简称'].count()
print(f'毛利率为负的股票一共有{m}只')


# 毛利率为负的股票竟然有31只，乐视网赫然在列，贾布斯画好了饼，愿者上钩。对于毛利率为负的股票你还敢去买，除非你有内部消息，否则只能说你胆子很肥。

# In[139]:


get_data_plot('600890','2010-01-01','中房股份')


# In[140]:


get_data_plot('300104','2010-01-01','乐视网')
#这里的价格是前复权了
#把时间拉长，乐视网从2010年上市到2015年大牛市，五年时间翻了N倍，创造了创业板的神话，但是2018年又响起了周杰伦熟悉的歌声“又回到过去...”


# #### 利润同比

# In[141]:


data.sort_values('利润同比',ascending=False)[:10]


# In[142]:


get_data_plot('600425','2010-01-01','青松建化')
#青松建化今年各项财务指标表现不错，但是近两年走势都不如大盘。


# In[143]:


data.sort_values('利润同比',ascending=True)[:10]


# In[144]:


get_data_plot('000953','2010-01-01','ST河化')
#ST河化在股市低迷的时候反而表现比青松建化好
#各项财务指标一塌糊涂


# #### 每股收益

# In[145]:


#每股收益最高的十家股票
data.sort_values('每股收益',ascending=False)[:10]


# In[146]:


p=data.sort_values('每股收益',ascending=False)['收盘价'][:10].mean()
pe=data.sort_values('每股收益',ascending=False)['市盈率'][:10].mean()
print(f'每股收益最高的十只股票平均价格为{p}元，平均市盈率为{pe}')


# 可见市场其实还是相对理性的，经营业绩好的公司总会被人挖掘出来，给予合理的估值。

# In[147]:


#贵州茅台近八年的股价走势
get_data_plot('600519','2010-01-01','贵州茅台')
#茅台才叫真牛吧，2015年鸡犬升天的时候，它却稳如泰山，
#2016年后伴随着股灾收割机的开启，大量股票腰斩，它却不断创新高。
#这走势一看还以为是美股标普走势呢


# In[148]:


#每股收益最低的十只股票
data.sort_values('每股收益',ascending=True)[:10]


# 中兴通讯应该是这里面比较熟悉的名字了，不出意外，受中美“毛衣战”影响，2018年三季度财务数据全部变脸：
# 收入同比-23.26%，利润同比-285.93%，净利率-12.35，每股收益-1.732，估计是中美贸易战最大的受害者之一了。看看资本市场的反馈如何？

# In[149]:


#中兴通讯走势
get_data_plot('000063','2010-01-01','中兴通讯')


# 在深圳的时候，经常会听到华为中兴，像金庸天龙八部里面经常被提到的北乔峰南慕容，当然，乔峰可一直没把南慕容放在眼里。
# 中兴通讯2015年牛市的时候平平无奇，2017年因为5G概念，飞了一把，谁知2018年中美“毛衣战”飞来横祸，
# 股价被拦腰一斩，甚是惨淡（其实还好，也就回到2017年之前）。中美“毛衣战”算是黑天鹅事件了，至少2018年年初的时候很少有人预料到会演变到这一步田地，
# 后面解读的基本上都是马后炮。万物互联的时代一直在酝酿着，相信5G概念未来仍然会持续发酵，但是中兴仍然感觉力不从心，毕竟脖子被人掐住了，
# 未来能否借助5G的发展突破困局，拭目以待。

# #### 市值

# In[150]:


#总市值最大的十只股票
data.sort_values('总市值',ascending=False)[:10]


# In[151]:


#工商银行走势
get_data_plot('601398','2010-01-01','工商银行')


# 其实从2017年以来，宇宙第一大行走势一直比大盘好很多，整个市场低迷的时候，银行股反而成了护盘的重要推手，当然大金融概念也是炒了一波。

# In[152]:


def get_data(code,startdate):
    df=ts.get_k_data(code,start=startdate)
    df.index=pd.to_datetime(df.date)
    return df.close
df=pd.DataFrame()
df['sh']=get_data('sh','2011-01-01')
codes={'601398':'工商银行','601939':'建设银行','601288':'农业银行','601988':'中国银行'}
for code,name in codes.items():
    df[name]=get_data(code,'2011-01-01')
fig = plt.figure(figsize=(12,6))  
ax1 = fig.add_subplot(111)  
ax1.plot(df['工商银行'],color='r',label='工商银行')
ax1.plot(df['建设银行'],color='b',label='建设银行')
ax1.plot(df['农业银行'],color='g',label='农业银行')
ax1.plot(df['中国银行'],color='y',label='中国银行')
ax1.legend(loc=2)
ax2=ax1.twinx()
ax2.plot(df['sh'],color='k',label='上证指数')
plt.title('四大行'+'vs上证指数近几年走势',fontsize=15)
ax2.legend(loc=1)
plt.show()


# 四大行走势还是很相似的，毕竟业务结构和盈利模式差异不明显，其中建行由于盘子小，波动性可能更强些，流通股本只有96亿，
# 而工商银行、农业银行和中国银行分别为2696亿、2940亿和2107亿流通股本。

# In[153]:


def get_data(code,startdate):
    df=ts.get_k_data(code,start=startdate)
    df.index=pd.to_datetime(df.date)
    return df.close
df=pd.DataFrame()
df['上证指数']=get_data('sh','2011-01-01')
codes={'601398':'工商银行','601939':'建设银行','601288':'农业银行','601988':'中国银行'}
for code,name in codes.items():
    df[name]=get_data(code,'2010-01-01')
def logreturn(data):
    logret=pd.DataFrame()
    for code in data.columns:
        logret[code]=np.log(data[code]/data[code].shift(1))
        logret.index=data.index
    return logret[1:]
df=pd.DataFrame()
df['上证指数']=get_data('sh','2011-01-01')
codes={'601398':'工商银行','601939':'建设银行','601288':'农业银行','601988':'中国银行'}
for code,name in codes.items():
    df[name]=get_data(code,'2010-01-01')
logret=logreturn(df)
logret.head()


# In[154]:


logret.cumsum().plot(figsize=(12,6))
plt.title('四大行最近八年累积收益率情况',fontsize=15)
plt.show()


# In[155]:


def sum_return(r_sum):
    maxv=(r_sum.max()*100).round(2)
    minv=(r_sum.min()*100).round(2)
    meanv=(r_sum.mean()*100).round(2)
    stdv=(r_sum.std()*100).round(2)
    for i in range(len(r_sum.columns)):
        print(f'{r_sum.columns[i]}最高收益率为{maxv[i]}%,最低收益率{minv[i]}%,平均收益率{meanv[i]}%,标准差{stdv[i]}%')


# In[156]:


r_sum=logret.cumsum()
sum_return(r_sum)


# 假设从2011年1月1日（若无交易日顺延）开始买入四大行，持有到今天。
# 区间最高收益率：建行为113.61%，工行为99.33%，农行91.72%，中行为79.53%，
# 而上证指数为59.39%；最低收益率：建行为-8.31%，工行为-9..67%，农行-6.49%，中行为-15.33%，
# 而上证指数为-38.04%.从标准差来看，建行波动最大。可以使用夏普率来比较，此处不展开分析。

# In[157]:


#总市值最小的十只股票
data.sort_values('总市值',ascending=True)[:10]


# In[158]:


df=pd.DataFrame()
df['上证指数']=get_data('sh','2011-01-01')
codes={'300028':'金亚科技','002323':'*ST百特','002260':'*ST德奥','300029':'天龙光电'}
for code,name in codes.items():
    df[name]=get_data(code,'2010-01-01')
logret=logreturn(df)
r_sum=logret.cumsum()
sum_return(r_sum)


# In[160]:


r_sum.plot(figsize=(12,6))
plt.title('市值最小的四只股票vs上证指数累积收益率',fontsize=15)
plt.show()


# 上证指数最高收益率为59.39%,最低收益率-38.04%,平均收益率-4.58%,标准差20.39%;  
# 金亚科技最高收益率为156.95%,最低收益率-256.7%,平均收益率-19.74%,标准差57.1%;  
# \*ST百特最高收益率为94.0%,最低收益率-191.41%,平均收益率-10.21%,标准差37.39%;  
# \*ST德奥最高收益率为236.79%,最低收益率-84.87%,平均收益率45.59%,标准差80.5%;  
# 天龙光电最高收益率为17.17%,最低收益率-187.58%,平均收益率-100.79%,标准差43.49%。  
# 
# 不难发现，从区间累积收益率来看，除了天龙光电外，其余三只小市值股票最高收益率均高过上证指数，
# 其中金亚科技和*ST德奥也高于四大行；但是，这三只股票的的区间累积收益率和标准差都明显大于四大行和上证指数。
# 特别是把时间拉长来看，投资这只极小盘股很容易出现过山车，有种“辛辛苦苦奋斗十年，一夜之间回到解放前”的感觉。

# ### 选择股票组合
# 选股就是不断剔除股票，留下自己“中意”股票的过程。针对上述基本面和交易数据设置参数和过滤值，剔除掉大部分股票。
# 注意，由于这里用到的基本面数据仅仅是2018年三季度的，企业的经营是动态演进的，市场交易频率更高，
# 因而对股票的筛选也应该是一个动态的过程，这里只是给出一个静态的思路，以供参考，所选股票也不构成投资建议，切记！

# In[179]:


#设置参数和过滤值(根据需要不断调整)
#市盈率>0
pe0=data['市盈率']>0
pe1=data['市盈率']<20
#市净率>0
pb0=data['市净率']>0
pb1=data['市净率']<2
#每股公积金>=1
res = data['每股公积'] >= 3
#流通股本<=20亿 
out = data['流通股'] <= 20
#每股收益>=1元 
eps = data['每股收益'] >= 1 
#总市值<500亿 
mktcap = data['总市值'] <= 500 
#收入同比正数
rev=data['收入同比']>15
#利润同比
profit=data['利润同比']>15
#净利率>5%
npr=data['净利率']>15
#取并集结果:

select = res & out & eps & mktcap & rev & pe0 &pe1 & pb0  & profit & npr
port= data[select] 
port

