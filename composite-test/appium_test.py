import os
import unittest
import copy
import time
import pytest

from appium import webdriver
from selenium.common.exceptions import WebDriverException

ANDROID_BASE_CAPS = {
    # 'app': os.path.abspath('../apps/ApiDemos-debug.apk'),
    # 'appPackage': 'com.xinpianchang.newstudios.enterprise',
    # "appActivity": "com.xinpianchang.newstudios.activity.MainActivity",
    'appPackage': 'com.tencent.mm',
    "appActivity": '.ui.LauncherUI',
    'automationName': 'UIAutomator2',
    'platformName': 'Android',
    # 'platformVersion': os.getenv('ANDROID_PLATFORM_VERSION') or '8.0',
    # 'deviceName': os.getenv('ANDROID_DEVICE_VERSION') or 'Android Emulator',
    'noReset': True,
    'appium:dontStopAppOnReset': True
}
# EXECUTOR = 'http://127.0.0.1:4723/wd/hub'
EXECUTOR = 'http://192.168.103.101:4723/wd/hub'

class TestAndroidMMScanQr():
    

    def test_should_create_and_destroy_android_session(self):
        caps = copy.copy(ANDROID_BASE_CAPS)
        caps['name'] = 'test scan qr code'

        self.driver = webdriver.Remote(
            command_executor=EXECUTOR,
            desired_capabilities=caps
            
        )
        self.driver.implicitly_wait(15)
        self.driver.find_element(value='com.tencent.mm:id/grs').click()
        self.driver.implicitly_wait(2)
        self.driver.find_elements(value='com.tencent.mm:id/iwc')[2].click()

        