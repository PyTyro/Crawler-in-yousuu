from urllib import request
from bs4 import BeautifulSoup
from multiprocessing import Pool
import re
import csv
import time
import pickle

def myCrawler(i):
    if i % 100 == 0:
        #完成进度
        print('Finished %.2f %%' % (i / 1500))
    try:
        download_url = 'http://www.yousuu.com/book/' + str(i)
        head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        req = request.Request(url=download_url, headers=head)
        response = request.urlopen(download_url)

        soup = BeautifulSoup(response, 'lxml')

        # 评分人数
        text2 = soup.find_all('div', class_='ys-book-averrate xs-align-left')[0].find('small').text
        numScore = ''.join(re.findall('[0-9]', text2))
        numScore = ''.join(numScore.split())
        if int(numScore) <= 50:
            return []

        # 输出作者,字数,章节数和最后更新时间
        text = soup.find_all('ul', class_='list-unstyled list-sm')
        x = text[0].find_all('li')
        author = x[0].find('a').text
        author = ''.join(author.split())
        sumChr = x[1].text
        sumChr = ''.join(re.findall('[0-9]', sumChr))
        sumChr = ''.join(sumChr.split())
        sumChapter = x[2].text
        sumChapter = ''.join(re.findall('[0-9]', sumChapter))
        sumChapter = ''.join(sumChapter.split())
        time = re.split(' ', x[4].text)[1]
        time = ''.join(time.split())

        # 评分
        text1 = soup.find_all('span', style='font-size:20px;color:#4d7bd6')
        point = ''.join((text1[0].text).split())

        # 书名
        bookname = soup.find_all('span', style='font-size:18px;font-weight:bold;')[0].text
        bookname = ''.join(bookname.split())

        # 类型
        type_ = soup.find_all('a', class_='tag category')[0].text
        type_ = ''.join(type_.split())

        return [i, str(bookname), str(type_), str(author), int(sumChr), int(sumChapter), str(time), int(numScore), float(point)]
    except:
        return []

def isEmpty(x):
    return len(x) != 0

if __name__ == '__main__':

    res1 = []

    p = Pool(processes=16)
    #res1 = p.map(myCrawler, list(range(1,101)))
    for i in range(1,150001):
        res = p.apply_async(myCrawler, (i,))
        res1.append(res)
    p.close()
    p.join()
    res1 = [x.get() for x in res1]
    res1 = list(filter(isEmpty, res1))

    with open('C:/code/text.txt', 'wb') as f:
        pickle.dump(res1, f)

    # with open("C:/code/text.txt", "rb") as f:
    #     a = pickle.load(f)
    #     print(a)

    with open('C:/code/test.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['优书网序号', '书名', '类型', '作者', '字数', '章节数', '最后更新时间', '评价人数', '评分'])
        writer.writerows(res1)
