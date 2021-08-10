
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """统计次数结果"""
    s = ''
    for k, v in terminalreporter.stats.items():
        if k != '':
            s += f'{k}: {len(v)}, '
    s = s[:-2]
    with open('.env', 'w') as f:
        f.write(f'RESULTS="{s}"')