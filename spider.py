from bs4 import BeautifulSoup
from cmd import Cmd
from unrar import rarfile
import requests
import os
import progressbar
import shutil

Url = 'http://www.cdfangxie.com'
pdf_file = 'file/'
rar_file_name = pdf_file + 'file.rar'


class Client(Cmd):
    prompt = '输入项目编号获取详情>'

    def preloop(self):
        shutil.rmtree(pdf_file)  # 清空目录避免影响
        print('正在获取最近项目...')
        url = Url + '/Infor/type/typeid/36.html'
        res = getHtml(url)
        res = res.find("div", class_="right_cont").find('ul', class_='ul_list').find_all('li')
        proj = getProj(res)
        self._proj = proj
        projname = [item['name'] for item in proj]
        projname = '\r\n'.join(projname)
        print(projname)

    def do_exit(self, arg):
        shutil.rmtree(pdf_file)  # 清空目录避免影响
        return True  # 返回True，直接输入exit命令将会退出

    def default(self, line):
        if (line.isdigit() and int(line) > 0 and int(line) <= len(self._proj)):
            index = int(line)
            proj = self._proj[index - 1]
            res = getHtml(Url + proj['href'])
            file_src = res.find('a', onclick="countHit(this)")['href']
            getFile(file_src, rar_file_name)
            unRar(rar_file_name)
            openFile(pdf_file)
        else:
            print('请输入正确编号')


def getFile(file_src, filename):
    isExists = os.path.exists(pdf_file)
    if not isExists:
        os.mkdir(pdf_file)
    response = requests.get(file_src, stream=True)
    chunk_size = 1024  # 单次请求最大值
    content_size = int(response.headers['content-length'])  # 内容体总大小
    print('下载:%s' % (file_src))
    with open(filename, "wb") as file:
        done_file = 0
        progress = progressbar.ProgressBar(max_value=content_size)
        for data in response.iter_content(chunk_size=chunk_size):
            file.write(data)
            done_file = len(data) + done_file
            progress.update(done_file)


def openFile(file_dir):
    files = os.listdir(file_dir)
    for file in files:
        if file.endswith('.pdf'):
            abs_path = os.path.dirname(os.path.realpath(__file__)) + "/" + file_dir + file
            os.startfile(abs_path)


def unRar(filename):
    print('正在解压...')
    file = rarfile.RarFile(filename)  # 这里写入的是需要解压的文件，别忘了加路径
    file.extractall(pdf_file)  # 这里写入的是你想要解压到的文件夹


def getHtml(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html5lib")
    return soup


def getProj(res):
    data = [{"name": li.get_text('||', strip=True), "href": li.find('a')['href']} for li in res if li.find('a')]
    return data


if __name__ == '__main__':
    os.system('cls')
    client = Client()
    client.cmdloop()
