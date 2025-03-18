from mcp.server.fastmcp import FastMCP
import os
import logging
import httpx

# 创建日志器
logger = logging.getLogger()
# 设置日志级别
logger.setLevel(logging.INFO)

# 创建控制台处理器（StreamHandler）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建文件处理器（FileHandler）
file_handler = logging.FileHandler('weather-mcp-server-python.log', mode='a')
file_handler.setLevel(logging.INFO)

# 创建日志格式器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 将格式器添加到处理器
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到日志器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Initialize FastMCP server
mcp = FastMCP("weather")

API_KEY = os.environ['WEATHER_API_KEY']

@mcp.tool()
def get_weather(city: str) -> str:
    """
    获取某个城市的天气

    Args:
    city: 城市
    """

    city_search_url = "https://geoapi.qweather.com/v2/city/lookup"
    weather_url = "https://devapi.qweather.com/v7/weather/now"

    logging.info(f"开始获取天气，城市：{city}")

    try:
        city_response = httpx.get(
            city_search_url,
            params={"location": city, "key": API_KEY},
            timeout=10
        )
        city_response.raise_for_status()
        city_data = city_response.json()
        logging.info(f"城市搜索接口返回结果：{city_data}")

        location_id = city_data.get("location", [{}])[0].get("id")
        if not location_id:
            logging.info("未能获取到城市的 locationId")
            return ""

        logging.info(f"城市的 locationId 为：{location_id}")
    except Exception as e:
        logging.error(f"获取城市 locationId 失败: {e}")
        return ""

    try:
        weather_response = httpx.get(
            weather_url,
            params={"location": location_id, "lang": "zh", "key": API_KEY},
            timeout=10
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        logging.info(f"天气接口返回结果：{weather_data}")

        now = weather_data.get("now", {})
        if not now:
            logging.info("天气数据缺失")
            return ""

        # 直接返回格式化的天气信息
        forecast = f"""
            观测时间: {now.get("obsTime", "")}
            温度: {now.get("temp", "")}°C
            体感温度: {now.get("feelsLike", "")}°C
            天气状况: {now.get("text", "")}
            风向: {now.get("windDir", "")} ({now.get("wind360", "")}°)
            风速: {now.get("windSpeed", "")} km/h
            风力等级: {now.get("windScale", "")}
            相对湿度: {now.get("humidity", "")}%
            降水量: {now.get("precip", "")} mm
            气压: {now.get("pressure", "")} hPa
            能见度: {now.get("vis", "")} km
            云量: {now.get("cloud", '无数据')}
            露点温度: {now.get("dew", '无数据')}
        """
        return forecast
    except Exception as e:
        logging.error(f"获取天气信息失败: {e}")
        return ""

if __name__ == '__main__':
    mcp.run(transport='sse')