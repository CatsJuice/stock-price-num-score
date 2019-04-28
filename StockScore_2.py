import os
import pandas as pd
from tqdm import tqdm

class StockScore(object):

    def __init__(self, prefix, calculate_days, date_now, days):
        self.days = days                        # 进行统计的天数， 默认为5
        self.file_path_prefix = prefix          # 日线文件目录
        self.start = 0                          # 要计算哪一天， 默认从文件第一行开始计算
        self.calculate_days = calculate_days    # 要统计多少天的盈利率
        self.all_score = []                     # 统计某日的打分集合
        self.all_rate = []                      # 盈利率的统计结果集合
        self.date_now = date_now                # 输入最新的数据日期（对应文件第一行的最新日期）

    # 打分计算
    def calculate_score(self):
        # 1. 遍历所有股票
        # 1.1 读取文件目录
        file_list = os.listdir(self.file_path_prefix)
        self.all_score = []     # 重置打分集合

        # 1.2 迭代每个文件
        for j in tqdm(range(len(file_list))):
            filename = file_list[j]
            code = filename[0:6]    # 解析得到股票代码
            try:
                df = pd.read_csv(self.file_path_prefix + filename, encoding="gbk")
            except UnicodeDecodeError:
                print("Error While Opening File: " + filename)
                continue
            # 2. 读取文件， 进行解析
            # 2.1 选取文件的 x ~ y 行， x 为 self.start， y 为self.start + self.days + 1 (多取一天以用于比较)
            temp_arr = df[self.start: self.start + self.days + 2]
            datas = temp_arr.values
            # 2.2 判断数据是否完整， 如果不完整， 该股票不可进行统计, 跳出循环至下一条
            # 不完整数据： 1) 不足需要的天数[self.days]; 2) 所选数据的第一行日期[self.date_now]无误
            row_1 = df[0:1].values
            if len(datas) < self.days+1 or row_1[0][0] != self.date_now:
                print("文件：", filename, "数据不全， 跳过", end=';')
                continue
            # 2.3 判断该只股票的市值是否大于800亿， 如果大于800亿则跳过
            if row_1[0][14] > 8e10:     # 流通市值
                continue
            # 2.4 遍历筛选后的数组， 计算 [self.days] 天的总分：score
            score = 0
            for i in range(len(datas)):
                if i == 0 or i == len(datas)-1:     # 第一行用作参照，最后一行仅用作最后一行的比较， 都不参与计算
                    continue
                delta_price = float(datas[i][8]) if datas[i][8] != "None" else 0              # 价格变化   ['涨跌额']
                delta_num = int(datas[i][11]) - int(datas[i + 1][11])                         # 成交量变化 ['成交量']
                score += self.add_score(delta_price, delta_num)
            # 2.5 判断该日是否盈利
            # [ 在这里定义判断盈利的规则 ] 这里以当日的收盘价较前一天上涨定义为盈利
            delta_price = float(datas[0][8]) if datas[0][8] != "None" else 0
            increase = "YES" if delta_price > 0 else "NO"
            # 2.6 将当日结果以字典形式放入数组
            dic = {'code': code, 'date': datas[0][0], 'score': score, 'is_increase': increase}
            self.all_score.append(dic)

    # 计算加分
    def add_score(self, delta_price, delta_num):
        if delta_price > 0 and delta_num > 0:       # 价涨量增 +2
            return 2
        elif delta_price > 0 and delta_num < 0:     # 价涨量缩 +1
            return 1
        elif delta_price < 0 and delta_num > 0:     # 价跌量增 -2
            return -2
        elif delta_price < 0 and delta_num < 0:     # 价跌量缩 -1
            return -1
        else:
            return 0

    # 盈利率计算： 按分数得分计算盈利率
    def calculate_rate(self):
        count_dic = {}                                  # 记录每个分数的数量
        yes_dic = {}                                    # 记录每个分数盈利的数量
        rate_dic = {'DATE': self.all_score[0]['date']}  # 记录每个分数盈利的几率 [ yes_dic / count_dic * 100]
        for item in self.all_score:
            # yes_dic
            if item['is_increase'] == "YES":        # 如果盈利， yes_dic中追加新的数据
                yes_dic[item['score']] = yes_dic[item['score']] + 1 if yes_dic.__contains__(item['score']) else 1
            # count_dic
            count_dic[item['score']] = count_dic[item['score']] + 1 if count_dic.__contains__(item['score']) else 1

        for key in count_dic:
            # 判断 yes_dic 有没有[key] 这个键， 避免报错
            rate_dic[key] = str(yes_dic[key] / count_dic[key] * 100) + "%" if yes_dic.__contains__(key) else str(0) + "%"
        self.all_rate.append(rate_dic)

    # 输出器
    def output(self):
        '''
        define output format here
        :return: None
        '''
        new_arr = []
        for item in self.all_rate:
            i = -10
            temp_dic = {'DATE': ''}
            for j in range(21):
                temp_dic[i] = '0%'
                i += 1
            for key in item:
                temp_dic[key] = item[key]
            new_arr.append(temp_dic)
        for i in new_arr:
            # 数据小数处理
            for key in i:
                # 小数处理
                if key == "DATE":
                    continue
                split_str = i[key].split('.')
                # 判断是不是整数
                if len(split_str) == 1:
                    if len(str(i[key][:-1])) < 3:
                        # 整数不足3位前面补0
                        i[key] = "0" * (3 - len(str(i[key][:-1]))) + str(i[key])
                    i[key] = str(i[key][:-1]) + ".00%"
                else:
                    left = split_str[0]
                    if len(left) < 3:
                        # 整数不足3位前面补0
                        left = "0" * (3 - len(left)) + str(left)
                    right = split_str[1]
                    right = right[:-1]  # 去%
                    if len(right) >= 2:
                        right = right[0:2]
                    else:
                        right = str(right) + "0"
                    i[key] = str(left) + "." + str(right) + "%"
            print(i)

    # 控制器
    def controll(self):
        for i in range(self.calculate_days):
            print("正在统计第", i+1, "天的盈利率")
            self.calculate_score()      # 统计分数
            self.calculate_rate()       # 计算盈利率
            self.start += 1             # 从下一天开始计算
            print()
            print(self.all_score)
        print()
        self.output()


if __name__ == '__main__':
    # 修改以下参数
    prefix = 'F:\\files\\sharesDatas\\kline\\'          # 网易财经日线数据文件前缀
    date_now = '2019-04-26'                             # 最新数据的第一个日期
    days = 5                                            # 加分的天数
    calculate_days = 20                                 # 演算天数

    ss = StockScore(prefix=prefix, calculate_days=calculate_days, date_now=date_now, days=days)     # 计算20天， 加分为5日的总分
    ss.controll()