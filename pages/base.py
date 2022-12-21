from selenium import webdriver

class Base():
    def __init__(self, driver=None):
        '''
        '''
        if not driver:
            options = webdriver.ChromeOptions()
            # todo: 远程or本地 配置文件
            # self.driver = webdriver.Remote('http://192.168.3.89:4444', options=options)
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver = driver

    def get_computed_style(self, elem, pseudo, prop):
        '''
        return window.getComputedStyle(document.querySelector('.okButton'),':after').getPropertyValue('content');
        '''
        # script = "return window.getComputedStyle(document.querySelector('{}'),'{}').getPropertyValue('{}');".format(css_selector, pseudo, prop)
        script = "return window.getComputedStyle(arguments[0],'{}').getPropertyValue('{}');".format(pseudo, prop)
        # print(script)
        return self.driver.execute_script(script, elem)

    
