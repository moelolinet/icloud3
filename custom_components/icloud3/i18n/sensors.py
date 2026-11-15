"""传感器友好名称（sensor friendly name）的中文显示。

传感器名是 ``"<设备名> <传感器类型>"``，例如 ``"Gary iPhone Battery"``。
``entity_id`` / ``unique_id`` 来自 devicename 与传感器键，与这里无关，所以只翻译
末尾的传感器类型词，设备名保持原样。
"""

from __future__ import annotations

from .core import is_chinese, text

# 传感器类型词 -> 中文
SENSOR_WORD = {
    "BatteryStatus": "电池状态",
    "Battery": "电池",
    "Name": "名称",
    "Badge": "徽章",
    "Info": "信息",
    "Interval": "间隔",
    "LastLocated": "上次定位",
    "LastUpdate": "上次更新",
    "NextUpdate": "下次更新",
    "TravelTime (hh:mm)": "行程时间（时:分）",
    "TravelTime (min)": "行程时间（分钟）",
    "TravelTimeMin": "行程时间（分钟）",
    "TravelTime": "行程时间",
    "ArrivalTime": "到达时间",
    "ZoneDistance": "区域距离",
    "HomeDistance": "距家距离",
    "MovedDistance": "移动距离",
    "CalcDistance": "计算距离",
    "WazeDistance": "Waze 距离",
    "Distance": "距离",
    "Direction": "方向",
    "ZoneInfo": "区域信息",
    "Trigger": "触发",
    "ZoneFname": "区域友好名称",
    "ZoneName": "区域名称",
    "ZoneChanged": "区域变更",
    "LastZone": "上次区域",
    "Zone": "区域",
    "GPSAccuracy": "GPS 精度",
    "VerticalAccuracy": "垂直精度",
    "Altitude": "海拔",
}

# 长的词先匹配，避免 "TravelTime" 抢先吃掉 "TravelTime (min)"
_ORDERED = sorted(SENSOR_WORD, key=len, reverse=True)


def sensor_name(fname):
    """把 ``"Gary iPhone Battery"`` 显示成 ``"Gary iPhone 电池"``。"""
    if not is_chinese() or not isinstance(fname, str):
        return fname

    for word in _ORDERED:
        if fname.endswith(" " + word):
            return fname[: -len(word)] + SENSOR_WORD[word]
        if fname.endswith("（" + word + "）"):
            return fname[: -len(word) - 2] + "（" + SENSOR_WORD[word] + "）"

    return text(fname)
