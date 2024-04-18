
                                                       使用说明
                                                       
第一步：安装完python环境之后在pycharm上运行main.py

在终端运行pip install -r requirement.txt

第二步：打开游览器，输入http://127.0.0.1:5000/get_page_template ，等待执行完毕在本地生成brand_page_url.json

第三步：在输入http://127.0.0.1:5000/get_device_url ，等待执行完毕，在目录device_url_data下生成相应文件

注意：

1.可以该格式http://127.0.0.1:5000/get_device_url?brand=brand1&brand=brand2 ，限定查询的设备品牌

第四步：在输入http://127.0.0.1:5000/get_device_data ，在目录device_data下生成excel

注意：

1.可以该格式http://127.0.0.1:5000/get_device_data?brand=brand1&brand=brand2 ，限定查询的设备品牌

2.可以该格式http://127.0.0.1:5000/get_device_data?brand=brand1&limit_num=2 , 
限定爬取该品牌最新的2台,限制爬取设备数量会导致excel head会与全部设备爬取不同，
excel head是由爬取的设备所拥有的字段组成的，爬取一部分可能会有个别字段没有，
最终形成的excel head有所不同
3.每个品牌每连续爬取300台将休眠20秒，以及每爬取50台会临时保存一份excel

由于未使用代理，第三步大约耗时10分钟左右，第四步大约每10台耗时20秒左右，第四步容易
