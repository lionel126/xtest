# config/node.toml
java -jar selenium-server-4.3.0.jar  standalone  --config node.toml

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222  --user-data-dir='/path/to'


# node.toml
[node]
detect-drivers = false
[[node.driver-configuration]]
display-name = "Chrome"
stereotype = "{\"browserName\": \"chrome\",\"browserVersion\": \"103.0.5060.53\",\"goog:chromeOptions\": {\"debuggerAddress\": \"localhost:9222\"},\"pageLoadStrategy\": \"normal\",\"platformName\": \"MAC\",\"proxy\": {}}"


# # # 
debuggerAddress 指定chromedebugging port, 连接启动了的chrome


# ????
相对selector vs 绝对selector? elem.find_element() or driver.find_element()
execute_script: puppeteer支持, 可以传入element object. python 支持

# css selector
:is(.red, .yellow)    -> either
:not(.red) 