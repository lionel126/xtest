MALL v2 TEST

## 环境
python 3.9.5 -m venv venv
pip install -r requirements.txt

## 代理配置
export http_proxy=http://192.168.8.27:30001; export REQUESTS_CA_BUNDLE="./tmp/rootCA.crt"; export https_proxy=http://192.168.8.27:30001;
<!-- export curl_ca_bundle="./tmp/mitmproxy-ca-cert.pem"; -->
# 打印日志
pytest --log-cli-level=INFO <test-file.py>



# 问题
复用太差 结构修改后大量工作量: cart_list.data.skus [] => null
程序写测试用例 本身bug

很早提测了 需求也在变动 不是说所有改动影响到测试 但是的确有一些
测什么
怎么测
接口测试效果怎么样？ 前端实际接入后遇到了接口设计的问题 

case 怎么写：
试探

# 
并发用券/ticket
第三方服务超时（5s）：商品库/支付...

# todo:
测试用例复用
不同storeCode ticket/coupon相同

多sku/pku/storeCode 下单
购物车下单

传None/不传/传空值？？ requests封装 None和不传的区别

# bug ??
promotiontag with storeCode
增加一个sku，优惠反而减少/？？？？？
~~rangeStoreCode 传"" 返 "0" ?? 怎么全部storeCode匹配？？~~
跨结算商户下单，部分支付。 满减优惠券不应该跨结算商户
