from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """
    获取城市的天气信息

    Args:
        city: 城市名称，如"北京"、"上海"
    """
    # 模拟天气数据（实际项目中调用天气 API）
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，22°C",
        "深圳": "小雨，28°C",
    }
    return weather_data.get(city, f"{city}的天气暂时无法获取")


# 测试工具
result = get_weather.invoke({"city": "北京"})
print(result)  # 输出: 晴天，25°C

# 查看工具信息
print(f"工具名称: {get_weather.name}")
print(f"工具描述: {get_weather.description}")
print(f"参数结构: {get_weather.args}")