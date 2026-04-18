#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
十二生肖预测分析脚本
基于：2026 马年规则 + 历史开奖数据 + 遗漏/频率统计
"""

# ---------- 固定规则数据 ----------
# 逆序生肖列表（与规则一致）
ZODIAC = ["马", "蛇", "龙", "兔", "虎", "牛", "鼠", "猪", "狗", "鸡", "猴", "羊"]

# 号码 1~49 的固定五行映射（根据用户提供规则补全）
NUMBER_WU_XING = {
    1: "水", 2: "火", 3: "火", 4: "金", 5: "金", 6: "土", 7: "土", 8: "木", 9: "木", 10: "火",
    11: "火", 12: "金", 13: "水", 14: "火", 15: "水", 16: "木", 17: "木", 18: "火", 19: "火", 20: "土",
    21: "土", 22: "水", 23: "水", 24: "木", 25: "木", 26: "金", 27: "金", 28: "土", 29: "土", 30: "水",
    31: "水", 32: "火", 33: "火", 34: "金", 35: "金", 36: "土", 37: "土", 38: "水", 39: "水", 40: "火",
    41: "火", 42: "金", 43: "金", 44: "水", 45: "水", 46: "木", 47: "木", 48: "火", 49: "火"
}

# 马年（2026）基础分配表：每个生肖对应的号码列表
BASE_ALLOCATION_2026 = {
    "马": [1, 13, 25, 37, 49],
    "蛇": [2, 14, 26, 38],
    "龙": [3, 15, 27, 39],
    "兔": [4, 16, 28, 40],
    "虎": [5, 17, 29, 41],
    "牛": [6, 18, 30, 42],
    "鼠": [7, 19, 31, 43],
    "猪": [8, 20, 32, 44],
    "狗": [9, 21, 33, 45],
    "鸡": [10, 22, 34, 46],
    "猴": [11, 23, 35, 47],
    "羊": [12, 24, 36, 48]
}

# 生肖到ID的映射（与现有系统保持一致）
ZODIAC_TO_ID = {
    "马": 1, "蛇": 2, "龙": 3, "兔": 4, "虎": 5, "牛": 6,
    "鼠": 7, "猪": 8, "狗": 9, "鸡": 10, "猴": 11, "羊": 12
}

# ID到生肖的映射
ID_TO_ZODIAC = {
    1: "马", 2: "蛇", 3: "龙", 4: "兔", 5: "虎", 6: "牛",
    7: "鼠", 8: "猪", 9: "狗", 10: "鸡", 11: "猴", 12: "羊"
}

# ---------- 分析函数 ----------
def analyze(history, current_year=2026):
    """返回统计数据字典"""
    total_draws = len(history)
    
    # 获取当前年份分配表（本例固定为2026马年）
    allocation = BASE_ALLOCATION_2026
    current_zodiac = "马"  # 2026本命生肖
    
    # 1. 统计各生肖出现次数
    freq = {z: 0 for z in ZODIAC}
    for _, z, _ in history:
        freq[z] += 1
    
    # 2. 计算遗漏期数
    # 按期号降序排列，找到每个生肖最近一次出现的期号
    sorted_history = sorted(history, key=lambda x: x[0], reverse=True)
    last_seen = {}
    for period, z, _ in sorted_history:
        if z not in last_seen:
            last_seen[z] = period
    latest_period = sorted_history[0][0]
    missing = {z: latest_period - last_seen.get(z, latest_period) for z in ZODIAC}
    
    # 3. 统计五行分布
    wuxing_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    for _, _, num in history:
        wx = NUMBER_WU_XING[num]
        wuxing_count[wx] += 1
    
    # 4. 理论概率
    theory_prob = {z: (5/total_draws if z == current_zodiac else 4/total_draws) for z in ZODIAC}
    
    return {
        "total": total_draws,
        "freq": freq,
        "missing": missing,
        "wuxing": wuxing_count,
        "theory": theory_prob,
        "current_zodiac": current_zodiac,
        "allocation": allocation
    }

def predict_next(stats):
    """根据统计结果给出下一期预测建议"""
    freq = stats["freq"]
    missing = stats["missing"]
    total = stats["total"]
    theory = stats["theory"]
    
    # 计算每个生肖的“推荐指数”：遗漏权重 + 频率偏差权重
    # 公式：推荐指数 = 遗漏期数归一化值 * 0.6 + 频率负偏差归一化值 * 0.4
    max_missing = max(missing.values())
    max_freq_dev = max([(theory[z] - freq[z]/total) for z in ZODIAC])
    
    scores = {}
    for z in ZODIAC:
        # 遗漏得分
        miss_score = missing[z] / max_missing if max_missing > 0 else 0
        # 频率偏差得分（实际低于理论越多分越高）
        freq_dev = theory[z] - freq[z] / total
        dev_score = freq_dev / max_freq_dev if max_freq_dev > 0 else 0
        # 综合得分
        scores[z] = miss_score * 0.6 + dev_score * 0.4
    
    # 排序
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # 五行建议：找出出现次数最少的五行
    wx = stats["wuxing"]
    min_wx = min(wx, key=wx.get)
    
    return {
        "top_zodiacs": sorted_scores[:3],
        "suggest_wuxing": min_wx,
        "allocation": stats["allocation"]
    }

def print_report(stats, prediction):
    """打印分析报告"""
    print("=" * 60)
    print(f"十二生肖预测分析报告 (基于 {stats['total']} 期数据)")
    print(f"当前本命生肖: {stats['current_zodiac']} (拥有5个号码)")
    print("=" * 60)
    
    # 频率表
    print("\n【生肖频率统计】")
    print(f"{'生肖':<4} {'出现次数':<6} {'理论次数':<6} {'偏差':<6} {'遗漏期数':<6}")
    print("-" * 40)
    for z in ZODIAC:
        actual = stats["freq"][z]
        theory_cnt = stats["theory"][z] * stats["total"]
        dev = actual - theory_cnt
        miss = stats["missing"][z]
        print(f"{z:<4} {actual:<6} {theory_cnt:<6.1f} {dev:+.1f}     {miss:<6}")
    
    # 五行分布
    print("\n【五行分布】")
    wx = stats["wuxing"]
    total = stats["total"]
    for w in ["金", "木", "水", "火", "土"]:
        cnt = wx[w]
        print(f"{w}: {cnt} 次 ({cnt/total*100:.1f}%)")
    
    # 预测建议
    print("\n【预测建议】")
    print(f"推荐关注五行: {prediction['suggest_wuxing']} (出现次数最少)")
    print("综合推荐生肖 (按优先级):")
    for i, (z, score) in enumerate(prediction["top_zodiacs"], 1):
        numbers = prediction["allocation"][z]
        wuxing_str = ", ".join(f"{n}({NUMBER_WU_XING[n]})" for n in numbers)
        print(f"  {i}. {z} (得分: {score:.3f}) -> 号码: {wuxing_str}")
    
    print("\n※ 以上分析仅供统计参考，不保证未来结果。")

def convert_history_data(history_data):
    """
    转换历史数据格式，使其与分析函数兼容
    输入: 前端传递的历史数据列表，每个元素包含 {period, zodiac, number}
    输出: 分析函数需要的格式 [(期号, 生肖, 号码)]
    """
    converted = []
    for item in history_data:
        period = item.get('period', 0)
        zodiac = item.get('zodiac', '')
        number = item.get('number', 0)
        
        # 处理生肖格式（可能是ID或名称）
        if isinstance(zodiac, int) and 1 <= zodiac <= 12:
            zodiac_name = ID_TO_ZODIAC.get(zodiac, zodiac)
        else:
            zodiac_name = str(zodiac)
        
        converted.append((period, zodiac_name, number))
    return converted

# ---------- 主程序 ----------
if __name__ == "__main__":
    # 示例历史数据
    HISTORY_DATA = [
        (2026107, "马", 49),
        (2026106, "鸡", 22),
        (2026105, "兔", 28),
        (2026104, "马", 1),
        (2026103, "牛", 6),
        (2026102, "猪", 20),
        (2026101, "龙", 39),
        (2026100, "狗", 33),
        (2026099, "羊", 12),
        (2026098, "虎", 17),
        (2026097, "猴", 11),
        (2026096, "鼠", 43),
        (2026095, "猴", 35),
        (2026094, "虎", 17),
        (2026093, "兔", 40),
        (2026092, "牛", 6),
        (2026091, "马", 37),
        (2026090, "羊", 36),
        (2026089, "马", 49),
        (2026088, "龙", 27),
        (2026087, "蛇", 26),
        (2026086, "羊", 12),
        (2026085, "鼠", 19),
        (2026084, "兔", 16),
        (2026083, "虎", 5),
        (2026082, "龙", 27),
        (2026081, "虎", 17),
        (2026080, "龙", 3),
        (2026079, "猴", 35),
        (2026078, "鸡", 46),
        (2026077, "虎", 29),
        (2026076, "蛇", 2),
        (2026075, "狗", 33),
        (2026074, "鸡", 10),
        (2026073, "鸡", 34),
        (2026072, "鸡", 46),
        (2026071, "羊", 48),
        (2026070, "马", 25),
        (2026069, "羊", 24),
        (2026068, "猴", 23),
        (2026067, "虎", 5),
        (2026066, "马", 37),
        (2026065, "虎", 5),
        (2026064, "牛", 18),
        (2026063, "兔", 28),
        (2026062, "羊", 24),
        (2026061, "虎", 29),
        (2026060, "狗", 9),
        (2026059, "鸡", 10),
        (2026058, "鼠", 31),
        (2026057, "猴", 23),
        (2026056, "羊", 48),
        (2026055, "蛇", 14),
        (2026054, "羊", 48),
        (2026053, "龙", 15),
        (2026052, "蛇", 38),
        (2026051, "马", 1),
        (2026050, "猴", 23),
        (2026049, "马", 13),
        (2026048, "羊", 24),
        (2026047, "兔", 39),
        (2026046, "兔", 3),
        (2026045, "蛇", 1),
        (2026044, "猪", 19),
        (2026043, "蛇", 13),
        (2026042, "虎", 16),
        (2026041, "马", 36),
        (2026040, "虎", 28),
        (2026039, "羊", 11),
        (2026038, "鼠", 42),
        (2026037, "猪", 43),
        (2026036, "蛇", 1),
        (2026035, "兔", 27),
        (2026034, "猪", 19),
        (2026033, "牛", 41),
        (2026032, "鼠", 6),
        (2026031, "龙", 26),
        (2026030, "牛", 41),
        (2026029, "蛇", 1),
        (2026028, "兔", 3),
        (2026027, "鸡", 45),
        (2026026, "猪", 19),
        (2026025, "蛇", 37),
        (2026024, "虎", 28),
        (2026023, "羊", 47),
        (2026022, "鼠", 18),
        (2026021, "鼠", 42),
        (2026020, "马", 12),
        (2026019, "猴", 46),
        (2026018, "兔", 39),
        (2026017, "狗", 32),
        (2026016, "鼠", 6),
        (2026015, "猪", 31),
        (2026014, "龙", 26),
        (2026013, "蛇", 1),
        (2026012, "羊", 11),
        (2026011, "羊", 11),
        (2026010, "兔", 27),
        (2026009, "虎", 28),
        (2026008, "鸡", 21),
        (2026007, "牛", 41),
        (2026006, "蛇", 13),
        (2026005, "猪", 43),
        (2026004, "鸡", 45),
        (2026003, "鸡", 9),
        (2026002, "猴", 22),
        (2026001, "牛", 29),
        (2026108, "狗", 45),   # 新增最新一期
    ]
    
    # 执行分析
    stats = analyze(HISTORY_DATA, current_year=2026)
    pred = predict_next(stats)
    print_report(stats, pred)
