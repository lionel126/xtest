MALL v2 TEST

## 代理配置
export http_proxy=http://192.168.8.27:8088;
export curl_ca_bundle="./mitmproxy-ca-cert.pem"; export https_proxy=http://192.168.8.27:8088;

# 打印日志
pytest --log-cli-level=INFO <test-file.py>



# 问题
购物车：不支持同时选中或取消选中 没法反选？？

# 
并发用券/ticket
第三方服务超时（5s）：商品库/支付...

# todo:
测试用例复用