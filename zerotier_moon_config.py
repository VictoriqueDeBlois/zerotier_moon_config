#!/bin/python3

import json
import os


def mkdir(path):
    if os.path.exists(path) is not True:
        os.makedirs(path)


def load_json(file):
    with open(file, 'r') as fp:
        out = json.load(fp)
    return out


def save_json(obj, file):
    with open(file, 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, sort_keys=True, indent=4, ensure_ascii=False)


def download_zerotier():
    os.system('curl -s https://install.zerotier.com | sudo bash')


def get_global_ip():
    stream = os.popen('curl -s cip.cc')
    content = stream.readlines()
    ip = content[0]
    ip = ip.split(':')[-1].strip()
    return ip


def generate_moon(ip):
    home = os.environ['HOME']
    mkdir(os.path.join(home, 'zerotier'))

    os.system('zerotier-idtool initmoon /var/lib/zerotier-one/identity.public > ~/zerotier/moon.json')
    moon_config = load_json(os.path.join(home, 'zerotier/moon.json'))
    moon_config['roots'][0]['stableEndpoints'] = [f'{ip}/9993']
    save_json(moon_config, os.path.join(home, 'zerotier/moon.json'))

    stream = os.popen('cd ~/zerotier && zerotier-idtool genmoon moon.json')
    content = stream.readlines()
    content = content[0]
    moon_file = content.split(' ')[1]

    mkdir('/var/lib/zerotier-one/moon.d')
    os.system('sudo chown zerotier-one:zerotier-one /var/lib/zerotier-one/moon.d')
    os.system(f'sudo cp {moon_file} /var/lib/zerotier-one/moon.d')
    os.system(f'sudo chown zerotier-one:zerotier-one /var/lib/zerotier-one/moon.d/{moon_file}')

    return moon_file


def restart_service():
    os.system('sudo systemctl restart zerotier-one.service')


if __name__ == '__main__':
    print('获取ip地址')
    address = get_global_ip()
    print(address)

    print('安装zerotier')
    download_zerotier()

    print('生成moon文件')
    moon_file = generate_moon(address)
    moon_path = os.path.join(os.environ['HOME'], 'zerotier', moon_file)
    print(f'生成moon文件到: {moon_path}')

    print('重启服务')
    restart_service()
