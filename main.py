# -*- coding: utf-8 -*-
import urllib2
import json
import uuid
import ConfigParser
import subprocess


def get_rss(line):
    db = "DB"
    rss_exists = line.find(db)
    if (rss_exists >= 0):
        # return line[rss_exists-3:rss_exists+len(db)]
        return line[rss_exists - 2:rss_exists].replace(':', '').replace(' ', '')
    return "99"


def get_mac_da(line):
    mac_length = 20
    mac_source = line.find("DA:")
    if (mac_source >= 0):
        return line[mac_source + 3:mac_source + mac_length].replace(':', '').replace(' ', '')
    return ""


def get_mac_BSSID(line):
    mac_length = 23
    mac_source = line.find("BSSID:")
    if (mac_source >= 0):
        return line[mac_source + 6:mac_source + mac_length].replace(':', '').replace(' ', '')
    return ""


def get_mac_address_loc():
    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
    # mac = ':'.join(mac_num[i : i + 2] for i in range(0, 11, 2))
    mac = ''.join(mac_num[i: i + 2] for i in range(0, 11, 2))
    return mac


def get_bs_ch(line):
    ch_length = 5
    ch_source = line.find("CH:")
    if (ch_source >= 0):
        return line[ch_source + 3:ch_source + ch_length]
    return ""


def print_data(line):
    data = line.split(" ")
    date = data[0]
    time = data[1][0:8]

    rss = get_rss(line)
    mac_source = get_mac_da(line)
    mac_dest = get_mac_BSSID(line)
    # mac_loc= get_mac_address_loc()
    bs_ch = get_bs_ch(line)

    return (mac_source + "," + mac_dest + "," + rss + "," + bs_ch)


def get_config(node_s, node_ss):
    conf = ConfigParser.ConfigParser()
    conf.read("/probe/probe.conf")
    return conf.get(node_s, node_ss)


def main():
    sc = "1"
    ok = "200"
    loc_mac = get_mac_address_loc()
    print "本地MAC初始化:" + loc_mac
    url = get_config("global", "url")
    print "URL初始化:" + url
    tcp_cmd = get_config("global", "tcpcmd")
    print "tcpdump参数:" + tcp_cmd
    scheme = get_config("global", "scheme")
    print "方案参数:" + scheme
    dump_std = subprocess.Popen("tcpdump " + tcp_cmd, shell=True, stdout=subprocess.PIPE)
    try:
        while (1):
            # for line in fileinput.input():
            line = dump_std.stdout.readline()
            # line ="1a"
            if (len(line) > 200):
                line_upper = line.upper()
                # exit_code = os.system('ping www.baidu.com')
                # if not exit_code:
                if (scheme.strip() == sc):
                    # rec = print_data(line_upper)
                    # rec =rec+","+loc_mac
                    # print line_upper
                    data = {
                        "AP_MAC": loc_mac,
                        "DA_MAC": get_mac_da(line_upper),
                        "BSSID_MAC": get_mac_BSSID(line_upper),
                        "Db": get_rss(line_upper),
                        "CH": get_bs_ch(line_upper),
                    }
                    headers = {'Content-Type': 'application/json'}
                    request = urllib2.Request(url, headers=headers, data=json.dumps(data))
                    # if(urllib2.urlopen(request).getcode()==ok):
                    try:
                        response = urllib2.urlopen(request)
                    except Exception, e:
                        continue
                if (scheme == 2):
                    print "wait....."
    except KeyboardInterrupt:
        print("Program stopped by user")


if __name__ == '__main__':
    main();
