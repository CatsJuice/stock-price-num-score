import os
import pandas as pd

class StockScore(object):

    def __init__(self, prefix, calculate_days, best_num, date_now, days):
        self.days = days                        # 进行统计的天数， 默认为5
        self.file_path_prefix = prefix          # k 线文件目录
        self.start = 0                          # 要计算哪一天， 默认从文件第一行开始计算
        self.calculate_days = calculate_days    # 要统计多少天的盈利率
        self.best_num = best_num                # 选取最优的几只股票进行计算
        self.all_score = []                     # 统计某日的打分集合
        self.all_rate = []                      # 盈利率的统计结果集合
        self.date_now = date_now                #

    # 打分计算
    def calculate_score(self):
        # 1. 遍历所有股票
        # 1.1 读取文件目录
        fileList = os.listdir(self.file_path_prefix)
        self.all_score = []         # 初始化

        all_sum = len(fileList)
        flag_num = 0
        pre = 0
        cur = 0

        # 1.2 迭代每个文件
        for filename in fileList:
            # 绘制进度条
            flag_num += 1
            percent = flag_num * 100 // all_sum
            cur = percent
            if cur != pre:
                self.print_percent(percent)
                pre = cur

            code = filename[0:6]
            try:
                df = pd.read_csv(self.file_path_prefix + filename, encoding="gbk")
            except UnicodeDecodeError:
                print("Error while open file: " + filename)
                continue
            # 2. 读取文件， 进行解析
            # 2.1 选取文件的x-y行， x 为 self.start， y 为self.start + self.days + 2 (多取一天以用于比较)
            temp_arr = df[self.start:self.start + self.days + 2]
            datas = temp_arr.values
            # 2.2 判断数据是否完整， 如果不完整， 该股票不可进行统计, 跳出循环至下一条
            row_1 = df[0:1]
            row_1 = row_1.values
            if len(datas) < self.days+1 or row_1[0][0] != self.date_now:
                print("股票", code, "数据不全， 跳过", end=';')
                continue
            # 2.3 遍历筛选后的数组， 计算score
            score = 0
            for i in range(len(datas)):
                if i == 0 or i == len(datas)-1:     # 第一行用作参照，最后一行仅用作最后一行的比较， 都不参与计算
                    continue
                delta_price = float(datas[i][8]) if datas[i][8] != "None" else 0        # 价格变化
                delta_num = int(datas[i][11]) - int(datas[i + 1][11])                   # 成交量变化
                score += self.add_score(delta_price, delta_num)
            # 2.4 判断该日是否盈利
            delta_price = float(datas[0][8]) if datas[0][8] != "None" else 0
            increase = "YES" if delta_price > 0 else "NO"
            # 2.5 将当日结果以字典形式放入数组
            dic = {'code': code, 'date': datas[0][0], 'score': score, 'is_increase': increase}
            self.all_score.append(dic)

    # 计算加分
    def add_score(self, delta_price, delta_num):
        if delta_price > 0 and delta_num > 0:
            return 2
        elif delta_price > 0 and delta_num < 0:
            return 1
        elif delta_price < 0 and delta_num > 0:
            return -2
        elif delta_price < 0 and delta_num < 0:
            return -1
        else:
            return 0

    # 数组冒泡排序
    def bubble_sort(self):
        res = self.all_score
        n = len(res)
        for i in range(n - 1):
            for j in range(n - 1 - i):
                if res[j]['score'] > res[j + 1]['score']:
                    res[j], res[j + 1] = res[j + 1], res[j]
        self.all_score = res

    # 盈利率计算
    def calculate_rate(self):
        self.bubble_sort()
        # low
        count_yes = 0
        count_no = 0
        for i in range(self.best_num):
            # print(i + 1, self.all_score[i])
            if self.all_score[i]['is_increase'] == "YES":
                count_yes += 1
            else:
                count_no += 1
        rate_low = str(count_yes / (count_yes + count_no) * 100)+'%'

        # high
        count_yes = 0
        count_no = 0
        for i in range(self.best_num):
            # print(i + 1, self.all_score[len(self.all_score) - 1 - i])
            if self.all_score[len(self.all_score) - 1 - i]['is_increase'] == "YES":
                count_yes += 1
            else:
                count_no += 1
        rate_high = str(count_yes / (count_yes + count_no) * 100)+'%'

        dic = {'date': self.all_score[0]['date'], 'rate_low': rate_low, 'rate_high': rate_high}
        self.all_rate.append(dic)

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
        for item in self.all_rate:
            print(item)

    # 进度条打印
    def print_percent(self, n):
        print()
        print("[", end='')
        print('#' * n, end='')
        print(' ' * (100 - n), end='')
        print(']', n, '%', end=' ')


if __name__ == '__main__':
    # 修改以下参数
    prefix = 'F:\\files\\sharesDatas\\kline\\'
    date_now = '2019-04-26'
    days = 5
    calculate_days = 20
    best_num = 10

    ss = StockScore(prefix=prefix, calculate_days=calculate_days, best_num=best_num, date_now=date_now, days=days)   # 计算20天， 最优选5只， 加分为5日的总分
    ss.controll()