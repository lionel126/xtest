MALL v2 TEST

## 环境
python3.9 -m venv .venv
pip install -r requirements.txt

## 代理配置
export http_proxy=http://192.168.8.27:8000; export https_proxy=http://192.168.8.27:8000;
export REQUESTS_CA_BUNDLE="./tmp/mitmproxy-ca-cert.pem"; 
export SSL_CERT_FILE=./tmp/mitmproxy-ca-cert.pem
<!-- export CURL_CA_BUNDLE="./tmp/mitmproxy-ca-cert.pem"; -->
# 打印日志
pytest --log-cli-level=INFO <test-file.py>
# 符合设计
并发用券/ticket
第三方服务超时（5s）：商品库/支付...
跨结算商户下单，部分支付。 满减优惠券不应该跨结算商户
增加一个sku，优惠反而减少/？？？？？


autosummary: 默认不能生成module内的class/funtion等的子页面（比如包含实例方法） https://github.com/sphinx-doc/sphinx/issues/7912

# doc step:
1. sphinx-quickstart: 独立源文件和构建目录; 语言 zh_CN
2. 修改source/conf.py: path加入源项目目录(有注释掉的例子: 如果使用相对路径，是相对conf.py的目录), 添加插件
```
"sphinx.ext.autodoc", "sphinx.ext.autosummary"
```   
3. index.rst 写入autosummary配置
``` 
   .. autosummary::
      :toctree: modules
      :recursive: 

      path.to.module1
      module2
```
4.  make html: 由于最上面提到的原因，还不能自动生成class的页面，修改对应module.rst(添加一行toctree[: Dir])后重新执行: make html
```
   .. rubric:: Classes

   .. autosummary::
      :toctree: modules

      TestPassport
      URL
```

# 重新生成 doc
<!-- rm -rf build source/modules -->
rm -rf _build/* _modules/_modules

# 下单

前提条件
sku：状态(on_sale). 价格=0？限购 是否已购买/添加购物车？
删除多余的优惠券/ticket 影响最终价格计算

价格计算器怎么测？ 后端价格计算器有一套复杂的逻辑，并不是最便宜；
我也写一个价格计算器来测试？ 我写一个不一样的计算器 怎么保证算出来一样？ 如果跟后端实现写成一样的，那还测什么？
最终结果：几个商品 几个优惠券 几个兑换券 下单确认下价格。确保每次算出来价格是一样的 

# 问题
结构修改后大量工作量: cart_list.data.skus [] => null, get_skus(), validate 400
程序写测试用例 本身bug
很早提测了 需求也在变动 不是说所有改动影响到测试 但是的确有一些

测什么？接口测试定位 跟功能测试什么关系？各有什么侧重点？
怎么测
接口测试效果怎么样？ 前端实际接入后遇到了接口设计的问题 

case 怎么写：
试探

后记：
测了什么？ 这些用例都是测什么的 哪些测了 哪些没测
怎么知道测了什么？ 测试覆盖
# todo:
幂等性
测试用例复用
传None/不传/传空值？？ requests封装 None和不传的区别 
    不封装，每次写个请求都要去找文档，参数多的（创建优惠券）太麻烦
    封装，没办法覆盖所有参数的不传 -> 参数可变类型：None走默认值, 非None直接用
供应商处下单数&下载数 避免重复扣款
购物车sku有效/无效变化 与前端不同步


Aug 19: 下单接口修改：ticket的使用；
测试用例报错修复
- test/trade_test.py::TestPay::test_pay_succeeded
- test/trade_test.py::TestTradeSubmit::test_trade_submit[4]
- ticketValue 下单价格？ 发放？
- 买多个 ticket 500？