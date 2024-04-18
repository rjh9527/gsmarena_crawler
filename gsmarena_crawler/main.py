from flask import Flask, render_template, request, Response
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

from tools import read_brand_page_url, get_page_device_url, read_device_urls, store_in_json, get_device_info, \
    create_workbook, input_workbook, get_brand_url, get_brand_page_template, store_brand_page_url

app = Flask(__name__)


@app.route("/get_page_template", methods=["GET"])
def get_page_template():
    brand_url_map = get_brand_url()
    brand_page_urls = {}

    def generate_data():
        for brand, url in brand_url_map.items():
            yield f"开始获取{brand} Page URL模板\n"
            data = get_brand_page_template(brand, url)
            page_url = data["page_url"]
            max_page_num = data["max_page_num"]
            brand_page_urls[brand] = {
                "page_url_template": page_url,
                "max_page_num": max_page_num
            }
            yield f"成功获取{brand} Page URL模板\n\n"
            time.sleep(1)
        yield f"获取所有品牌Page URL模板完毕\n\n"
        store_brand_page_url(brand_page_urls)

    response = Response(generate_data(), content_type='text/event-stream; charset=utf-8')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    return response


@app.route("/get_device_url", methods=["GET"])
def get_device_url():
    brands = request.args.getlist("brand")
    limit_page_num = int(request.args.get("limit_page_num", 0))
    brand_page_url_map = read_brand_page_url()
    if brands:
        brand_page_url_map = {
            brand: brand_page_url_map.get(brand)
            for brand in brands if brand in brand_page_url_map
        }
    if not brand_page_url_map:
        return Response("未找到有效品牌")

    brand_device_url_map = {brand: [] for brand in brand_page_url_map.keys()}

    def generate_data():
        for brand, brand_map in brand_page_url_map.items():
            page_url_template = brand_map["page_url_template"]
            max_page_num = brand_map["max_page_num"]

            if page_url_template is None:
                yield f"{brand}的Page URL 是None！！！！！\n"
                continue

            for page_num in range(1, max_page_num + 1):
                if limit_page_num != 0 and page_num > limit_page_num:
                    yield f"{brand}已爬取到{page_num}页，超过限制{limit_page_num}页，停止爬取\n"
                    break

                url = page_url_template.format(page_num)
                device_url_list = get_page_device_url(url)
                if device_url_list is not None:
                    brand_device_url_map[brand].extend(device_url_list)
                    yield f"{brand}第{page_num}页成功获取到的设备url\n"
                else:
                    yield f"{brand}第{page_num}页获取到的设备url: {device_url_list}\n"
                #     # store_in_excel(all_data_dict_list, output_excel)
                time.sleep(2)  # 根据需要调整延迟
            yield f"\n=========={brand}获取完毕==========\n\n"
            store_in_json(brand_device_url_map[brand], brand)
        yield f"\n==========执行完毕==========\n\n"

    response = Response(generate_data(), content_type='text/event-stream; charset=utf-8')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    return response


@app.route("/get_device_data", methods=["GET"])
def get_device_data():
    brands = request.args.getlist("brand")
    limit_num = int(request.args.get("limit_num", 0))  # 限制爬取多少台

    brand_page_url_map = read_brand_page_url()
    if brands:
        brands = [brand for brand in brands if brand in brand_page_url_map]
    else:
        brands = list(brand_page_url_map.keys())

    if not brands:
        return Response("未找到有效品牌")

    def generate_data():
        for brand in brands:
            device_urls = read_device_urls(brand)
            if device_urls is None:
                yield f"\n{brand}没有对应的deivce url json 文件\n"
                continue
            head_dict = {"commodity": ["brand", "product"]}
            datas = []
            yield f"===开始爬取{brand}设备信息===\n"
            for index, device_url in enumerate(device_urls):
                if 0 < limit_num <= index:
                    yield f"{brand}已爬取到{index}台，超过限制{limit_num}台，停止爬取\n"
                    break
                result = (index + 1) % 10
                if result == 0:
                    yield f"{brand}已经爬取{index + 1}台设备\n"

                sleep_flag = (index + 1) % 300
                if sleep_flag == 0:
                    sleep_time = 20
                    yield f"\n====={brand}已经连续爬取{index + 1}台设备,进入{sleep_time}秒休眠=====\n\n"
                    time.sleep(sleep_time)

                head_dict, specs_info = get_device_info(device_url, head_dict)
                if specs_info is None:
                    yield f"{device_url}爬取失败！！！！！\n"
                    continue
                datas.append(specs_info)
                save_flag = (index + 1) % 50
                if save_flag == 0:
                    create_workbook(brand, head_dict)
                    input_workbook(brand, datas)
                time.sleep(1)
            yield f"===爬取{brand}设备信息完毕===\n\n"
            create_workbook(brand, head_dict)
            input_workbook(brand, datas)

    response = Response(generate_data(), content_type='text/event-stream; charset=utf-8')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    return response


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
