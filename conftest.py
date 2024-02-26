
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """统计测试结果写入文件 待jenkins发钉钉"""
    s = ''
    for k, v in terminalreporter.stats.items():
        if k != '':
            s += f'{k}: {len(v)}, '
    s = s[:-2]
    with open('.env', 'w') as f:
        f.write(f'RESULTS={s}\n')

# driver = None   # 定义一个全局driver对象

# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     # 什么时候去识别用例的执行结果呢？
#     # 后置处理 yield：表示测试用例执行完了
#     outcome = yield
#     rep = outcome.get_result()      # 获取测试用例执行完成之后的结果
#     if rep.when == 'call' and rep.failed:   # 判断用例执行情况：被调用并且失败
#         # 实现失败截图并添加到allure附件。截图方法需要使用driver对象，想办法把driver传过来
#         # 如果操作步骤过程中有异常，那么用例失败，在这里完成截图操作
#         img = driver.get_screenshot_as_png()
#         # 将截图展示在allure测试报告上
#         allure.attach(img, '失败截图', allure.attachment_type.PNG)

# # 自定义fixture实现driver初始化及赋值并且返回
# @pytest.fixture(scope='session', autouse=True)
# def init_driver():
#     global driver   # global变量，相当于给上面driver = None赋值了
#     if driver is None:
#         driver = webdriver.Chrome()
#     return driver