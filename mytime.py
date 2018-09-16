# coding=utf-8

import requests
import base64
import re
import json


def get_basic_auth_str(username, password):
    temp_str = username + ':' + password
    bytes_string = temp_str.encode(encoding="utf-8")
    encode_str = base64.b64encode(bytes_string)
    # decode_str = base64.b64decode(encode_str)
    return 'Basic ' + encode_str.decode()


def parse_cookies(str_cookies=''):
    _cookies = {}
    c_patt = re.compile('(.*?)=(.*)')
    for kv in str_cookies.split(';'):
        mat = c_patt.match(kv)
        _cookies[str(mat.group(1)).strip()] = str(mat.group(2)).strip()

    return _cookies


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


def main(ym):
    url = "http://psa.isoftstone.com/api/Attendance/Home/HomeApi/GetAttendanceList"
    payload = "YearMonth=%s" % ym

    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN",
        'authorization': "87e2e0de1aafca8d9afc460392ad2240106b352d",
        'cache-control': "no-cache",
        'connection': "Keep-Alive",
        'content-length': "17",
        'content-type': "application/x-www-form-urlencoded",
        'host': "psa.isoftstone.com",
        'key': "Attendance_Home_MyAttendance_View_GetAttendanceList",
        'origin': "http://psa.isoftstone.com",
        'referer': "http://psa.isoftstone.com/Attendance/Home/HomeView/Index",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        'x-requested-with': "XMLHttpRequest",
    }
	
	token = get_basic_auth_str(name, passwd)
    token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    # headers['authorization'] = token

    str_cookies = ".iPSA=5AAF8FC1B8989A57E1581C67E8369549B22849B58EE57B2CA0B129F3CAF9FF2B573915C92C497BA9535E36C21A778445E551FEC8B1D37079AB597DB836F86BD1B584C486A2816A456AEE7E64ACE14923; DomainName=lzzengc; UserName=Ek/4jFHJbg0=; IsJV=True; idsrv=CfDJ8MaMGgRH1RtDsbhcSI5XbTzF9VlXMvPGJX-rfQa1x2wja7VEDxBr7PTUtBRiyg9oojNPWAjfmp6bbeYdWTfpI9iAeL5uP7Ny1yyySoQLsIf_ugNAuWD4LDpwPaVEvuwgc97cH4CwvfSzf15i1K6HWNYfJxap36E6OGzVeaxbfSQo0QIyedH48gcAnmJv_LN7H6xxNhyD3Cr3plGDPAZsYj8yb1EdHqZMhUQbd7PjzgrypvhiULSeCK1DAD4lEBb_sMImUtofMDQlBU1i4bSG5XJC9TU4rjmJbvP_3Dqurf7A1Avaxot6-jIlLLmen41B_p3Gh32cA4tnqp1VCMf_CY4EjJogo5bKVRhw4eZADfroHszueq2HBVVv5JNwxE_3GIFY9CxyHR50AirdBC6e-Id83g8UP8prXG8oPKFBrk_1oD-61GFBCupl0Dp3xNvJYsCtIxtnsGDCfnD0iXR8HYB2mEJRrVMQrhnp0BXln8koHeGS06HdrkSMFD5PFDYZ5yBmJHrpNMag3ENuPVA8LrduaHb0M5f95f5krHNVR9co43gH9ts9qKLRTYkswzqG4OHUE6Mc_WOJbXK3gtS_93s; SESSION_THEME_KEY=red"
    cookies = parse_cookies(str_cookies)
    
    cookies['token'] = token
    response = requests.request("POST", url, data=payload, headers=headers, cookies=cookies)
    time_dic = json.loads(response.content)
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
    print "************* %s月工时统计 (%2d天) *************" % (mon, d_sum)
    print "绝对时长：%16s %16s" % (str("%d Min" % a_sum), str("%0.1f H" % (a_sum * 1.0 / 60)))
    print "应有工时：%16s %16s" % (str("%s Min" % (d_sum * 480)), str("%0.1f H" % (8.0 * d_sum)))
    print "有效工时：%16s %16s" % (str("%d Min" % t_sum), str("%0.1f H" % (t_sum * 1.0 / 60)))
    print "有效均值：%16s %16s" % (str("%d Min" % (t_sum / d_sum)), str("%0.1f H" % (t_sum * 1.0 / d_sum / 60)))
    print "有效均差：%16s %16s" % (str("%s Min" % (t_sum / d_sum - 480)), str("%0.1f H" % ((t_sum / d_sum - 480) * 1.0 / 60)))


# year_mon = raw_input("输入月份，如2018-07：\n")
year_mon = "2018-09"
main(year_mon)

