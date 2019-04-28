# stock-price-num-score
根据《胡立阳股票投资100招》给股票打分的盈利率


胡立阳根据股票的`价量关系`对股票进行打分， 而其打分的依据如下：

> **当日个股表现：**
> 
>（1）价涨量增 `+2` 分
>
>（2）价涨量缩 `+1` 分
>
>（3）价跌量增 `-2` 分
>
>（4）价跌量缩 `-1` 分
>
> 每日累计评分。你只要连续计算一个星期,以最高分或者是评分稳定增加的作为你投资的第一选择,因为那只个股具备了“价量配合”的上涨条件

根据这个打分标准， 不难计算每只股票某日的得分， 然后将所有得分排序即可， 这样能够得到某一天的所有股票打分， 而需要验证每只股票是否盈利， 这里我简单地判断后一天收盘价是否比当天高，所以能够得出每只股票是否盈利， 计算出当天得分前`n`只股票的盈利与否， 再用 盈利股票的只数 / n 即当天的盈利率；

以此类推`m`天可得出m天这一策略的盈利几率， 如下图是我得出的某一种可能：

![胡立阳打分标准盈利率](https://catsjuice.cn/index/src/markdown/stock/201904281250.png "胡立阳打分标准盈利率")

> **键值说明:**
> 
> `date`: 统计的日期
>
> `rate_low`: 打分最低的盈利几率
>
> `rate_high`: 打分最高的盈利几率

**文件列表说明**
- `StockScore.py`   计算每天前排名前n的股票的盈利率
- `StockScore_2.py` 计算每个分数的盈利率

**StockScore_2.py简易流程图**

![StockScore_2.py简易流程图](https://catsjuice.cn/index/src/markdown/stock/mind201904281842.jpg "StockScore_2.py简易流程图")
[流程图原图](https://catsjuice.cn/index/src/markdown/stock/mind201904281842.jpeg)

**下载**
- 下载`.zip`文件
- `git clone https://github.com/CatsJuice/stock-price-num-score.git`

**使用前提**
- Python 3.x
- 第三方库支持（`pandas`, `tqdm`）
    - `pip install pandas`
    - `pip install tqdm`
- 数据准备
    - 数据需要为网易财经的数据（因为字段名需要对应）
    - 网易财经的抓取在[https://github.com/CatsJuice/netease-stock-day-line.git](https://github.com/CatsJuice/netease-stock-day-line.git)
    - 也可以直接`git clone https://github.com/CatsJuice/netease-stock-day-line.git`
- 参数修改， 参数详情如下表

id | param | type | mean | demo
:--: | :--: | :--: | :--: | :--:
1 | `prefix` | str | 网易财经日线数据文件前缀 | `'F:\\files\\sharesDatas\\kline\\' `
2 | `date_now` |str| 最新数据的第一个日期, 对应爬取的最新数据表第一行的日期 | `'2019-04-26'` ; Format( `yyyy-mm-dd` )
3 | `days` | int | 加分的天数 | `5`
4 | `calculate_days` | int | 要统计的天数 | `20`
5 | `best_num` | int | 选出的最佳的天数 | `10`

`StockScore_2.py` 中， 市值大于800亿的不计入统计， 可在`LINE: ~43`修改如下：
```
# 2.3 判断该只股票的市值是否大于800亿， 如果大于800亿则跳过
if row_1[0][14] > 8e10:     # 流通市值
    continue
```
修改为
```
# 2.3 判断该只股票的市值是否大于800亿， 如果大于800亿则跳过
if row_1[0][14] > [change here]:     # 流通市值
    continue
```