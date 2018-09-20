# coding=utf-8

import requests
import json
import re
import uinf
from bs4 import BeautifulSoup


def parse_cookies(str_cookies=''):
    _cookies = {}
    c_patt = re.compile('(.*?)=(.*)')
    for kv in str_cookies.split(';'):
        mat = c_patt.match(kv)
        _cookies[str(mat.group(1)).strip()] = str(mat.group(2)).strip()

    return _cookies


def parse_headers(str_headers='', f_headers='headers.txt'):
    _str_headers = str_headers
    _headers = {}
    if not _str_headers:
        with open(f_headers, 'r') as fp:
            _str_headers = fp.read()

    h_patt = re.compile('(.*?):(.*)')
    for h_line in str(_str_headers).splitlines():
        # print h_line
        mat = h_patt.match(h_line)
        if mat:
            # print mat.groups()
            # noinspection PyBroadException
            try:
                # _headers[mat.group(1)] = urllib.unquote(mat.group(2))
                _headers[str(mat.group(1)).strip()] = str(mat.group(2)).strip()
            except:
                continue

    return _headers


def convert_t(t):
    t1 = int(t[0].split(':')[1]) + int(t[0].split(':')[0]) * 60
    t2 = int(t[1].split(':')[1]) + int(t[1].split(':')[0]) * 60
    _t = (t1, t2)
    return _t


def cal_tsum(t):
    if t[0] is None or t[1] is None:
        return 0, 0, 0

    t_valid_a = [("8:00", "12:00"), ("13:30", "17:30"), ("18:00", "24:00")]
    t_valid_b = [("8:00", "12:30"), ("14:00", "17:30"), ("18:00", "24:00")]
    t_valid_a = [convert_t(e) for e in t_valid_a]
    t_valid_b = [convert_t(e) for e in t_valid_b]
    t = convert_t(t)
    t_valid = t_valid_a if t[0] <= 480 else t_valid_b
    t_s = 0
    for e in t_valid:
        for ee in range(t[0], t[1]):
            if ee in range(e[0], e[1]):
                t_s += 1
    return t_s, 1, t[1] - t[0]


def get_time(ym, se):
    url = "http://psa.isoftstone.com/api/Attendance/Home/HomeApi/GetAttendanceList"
    payload = "YearMonth=%s" % ym

    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN",
        'cache-control': "no-cache",
        'content-type': "application/x-www-form-urlencoded",
        'host': "psa.isoftstone.com",
        'key': "Attendance_Home_MyAttendance_View_GetAttendanceList",
        'origin': "http://psa.isoftstone.com",
        'referer': "http://psa.isoftstone.com/Attendance/Home/HomeView/Index",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        'x-requested-with': "XMLHttpRequest",
    }

    # response = requests.request("POST", url, data=payload, headers=headers, cookies=cookies)
    r = se.post(url, data=payload, headers=headers)
    time_dic = json.loads(r.content)
    daily_time = time_dic['Data']['Result']['Days']

    t_sum = 0
    d_sum = 0
    a_sum = 0
    mon = int(ym.split('-')[-1])
    for ele in daily_time:
        s = ele['Day']
        if s.startswith(u'%s月' % mon):
            # s = r'9\u6708'
            # print s.decode('unicode_escape')
            t, d, a = cal_tsum((ele['First'], ele['Last']))
            t_sum += t
            d_sum += d
            a_sum += a

    print
    print "************* %s (%2d D) *************" % (ym, d_sum)
    print "%12s %12s %12s" % ("Absolute:", str("%d Min" % a_sum), str("%0.1f H" % (a_sum * 1.0 / 60)))
    print "%12s %12s %12s" % ("Needed:", str("%s Min" % (d_sum * 480)), str("%0.1f H" % (8.0 * d_sum)))
    print "%12s %12s %12s" % ("Valid:", str("%d Min" % t_sum), str("%0.1f H" % (t_sum * 1.0 / 60)))
    print "%12s %12s %12s" % ("Average:", str("%d Min" % (t_sum / d_sum)), str("%0.1f H" % (t_sum * 1.0 / d_sum / 60)))
    print "%12s %12s %12s" % ("Diff:", str("%s Min" % (t_sum / d_sum - 480)), str("%0.1f H" % ((t_sum / d_sum - 480) * 1.0 / 60)))


url = 'https://passport.isoftstone.com/?DomainUrl=http://ipsapro.isoftstone.com&ReturnUrl=%2fPortal%2f'
# url = urllib.unquote(url)
headers = parse_headers()
cookies = {}
payload = {"DomainUrl": "",
           "emp_DomainName": uinf.user,
           "emp_Password": uinf.passwd,
           "returnUrl": ""
           }

session = requests.Session()
r = session.post(url, headers=headers, data=payload)
print r.status_code, "POST", url

url = "http://ipsapro.isoftstone.com/portal/Special/hwkq"
headers = {'upgrade-insecure-requests': "1",
           'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
           'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
           'referer': "http://ipsapro.isoftstone.com/Portal",
           'accept-encoding': "gzip, deflate",
           'accept-language': "zh-CN,zh;q=0.8",
           'cache-control': "no-cache",
           }

r = session.request("GET", url, headers=headers)
print r.status_code, "GET", url
token = ""
soup = BeautifulSoup(r.content, "html.parser")
tk = soup.find(id='token')
if tk:
    token = tk.get('value')

url = "http://psa.isoftstone.com/Common/User/UserView/IntegrateLogin"
payload = {"callbackUrl": "http://psa.isoftstone.com/Attendance/Home/HomeView/Index",
           "tenant": "PSA",
           "token": token,
           "verifyUrl": "http://timesheet.isoftstone.com:9119/api/PSA/CheckLogin"
           }

headers = {"origin": "http://ipsapro.isoftstone.com",
           "upgrade-insecure-requests": "1",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
           "content-type": "application/x-www-form-urlencoded",
           "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
           "referer": "http://ipsapro.isoftstone.com/portal/Special/hwkq",
           "accept-encoding": "gzip, deflate",
           "accept-language": "zh-CN,zh;q=0.8",
           "cache-control": "no-cache"
           }

r = session.request("POST", url, data=payload, headers=headers)
print r.status_code, "POST", url
cookies = parse_cookies(r.request.headers['Cookie'])
print "Cookies:"
print json.dumps(cookies, indent=2)
print

year_mon = raw_input("输入月份，如\"2018-07\"：\n")
year_mon = "2018-09"
get_time(year_mon, session)
year_mon = "2018-08"
get_time(year_mon, session)
