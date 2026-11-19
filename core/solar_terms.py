"""二十四节气：日期、应季食物，以及匹配菜谱用的关键词 / 标签。

日期用的是常见的固定近似值（每年会差一两天，这里不追求精确）。
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SolarTerm:
    name: str
    month: int
    day: int
    season: str
    foods: tuple[str, ...]      # 传统应季食物（展示用）
    tags: tuple[str, ...]       # 匹配菜谱标签（兜底）
    keywords: tuple[str, ...]   # 匹配菜名（优先）

    @property
    def date_str(self) -> str:
        return f"{self.month:02d}-{self.day:02d}"


# 按一年中的先后顺序排列
SOLAR_TERMS: tuple[SolarTerm, ...] = (
    SolarTerm("小寒", 1, 6, "冬", ("腊八粥", "糯米饭"), ("清淡", "汤"), ("粥", "饭", "汤")),
    SolarTerm("大寒", 1, 20, "冬", ("八宝饭", "年糕"), ("甜",), ("饭", "糕", "甜")),
    SolarTerm("立春", 2, 4, "春", ("春饼", "萝卜"), ("素", "清淡"), ("饼", "萝卜", "菜")),
    SolarTerm("雨水", 2, 19, "春", ("春笋", "韭菜"), ("素", "清淡"), ("笋", "韭", "菜")),
    SolarTerm("惊蛰", 3, 6, "春", ("梨", "炒豆"), ("甜", "清淡"), ("梨", "豆")),
    SolarTerm("春分", 3, 21, "春", ("太阳糕", "春菜"), ("素", "清淡"), ("糕", "菜")),
    SolarTerm("清明", 4, 5, "春", ("青团", "馓子"), ("甜", "素"), ("糕", "团", "面")),
    SolarTerm("谷雨", 4, 20, "春", ("香椿", "谷雨茶"), ("素", "清淡"), ("椿", "蛋")),
    SolarTerm("立夏", 5, 6, "夏", ("立夏蛋", "蚕豆"), ("素", "快"), ("蛋", "豆")),
    SolarTerm("小满", 5, 21, "夏", ("苦菜", "麦仁"), ("素", "清淡"), ("菜", "粥")),
    SolarTerm("芒种", 6, 6, "夏", ("青梅", "粽子"), ("甜", "快"), ("梅", "粽", "米")),
    SolarTerm("夏至", 6, 21, "夏", ("夏至面", "凉粉"), ("快", "清淡"), ("面", "凉")),
    SolarTerm("小暑", 7, 7, "夏", ("莲藕", "黄鳝"), ("清淡", "汤"), ("藕", "鱼")),
    SolarTerm("大暑", 7, 23, "夏", ("羊肉汤", "绿豆汤"), ("汤", "清淡"), ("汤", "豆")),
    SolarTerm("立秋", 8, 8, "秋", ("炖肉", "贴秋膘"), ("肉",), ("肉", "炖", "鸡")),
    SolarTerm("处暑", 8, 23, "秋", ("鸭肉", "莲藕"), ("肉", "汤"), ("鸭", "藕")),
    SolarTerm("白露", 9, 8, "秋", ("米酒", "龙眼"), ("甜",), ("酒", "甜", "圆")),
    SolarTerm("秋分", 9, 23, "秋", ("秋菜", "螃蟹"), ("素", "清淡"), ("蟹", "菜")),
    SolarTerm("寒露", 10, 8, "秋", ("芝麻", "菊花酒"), ("甜", "素"), ("芝麻", "糕")),
    SolarTerm("霜降", 10, 23, "秋", ("柿子", "鸭子"), ("肉", "甜"), ("柿", "鸭")),
    SolarTerm("立冬", 11, 7, "冬", ("饺子", "羊肉汤"), ("肉", "汤"), ("羊", "牛", "汤", "鸡")),
    SolarTerm("小雪", 11, 22, "冬", ("腊肉", "糍粑"), ("肉",), ("腊", "肉", "汤")),
    SolarTerm("大雪", 12, 7, "冬", ("羊肉", "红薯粥"), ("肉", "汤", "清淡"), ("羊", "粥", "汤")),
    SolarTerm("冬至", 12, 22, "冬", ("饺子", "汤圆"), ("汤", "肉"), ("饺", "圆", "汤")),
)

_BY_NAME = {t.name: t for t in SOLAR_TERMS}


def find(name: str) -> SolarTerm | None:
    return _BY_NAME.get(name)


def current(today: date | None = None) -> SolarTerm:
    """根据日期判断当前节气。

    规则：找到最后一个「日期不晚于今天」的节气。
    1 月 1~5 日还没到小寒，属于上一年的冬至。
    """
    today = today or date.today()
    result = SOLAR_TERMS[-1]  # 冬至兜底

    for term in SOLAR_TERMS:
        if (term.month, term.day) <= (today.month, today.day):
            result = term
        else:
            break

    return result
