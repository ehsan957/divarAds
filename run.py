import requests, re
from bs4 import BeautifulSoup
from persiantools import digits
from persiantools.jdatetime import JalaliDate
import mysql.connector
import time

def grab_from_home_page(city, i=1):
    idset = set()
    url = "https://divar.ir/s/"+city+"/car?page="+str(i)
    headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    
    while True:
        try:
            source = requests.get(url, headers=headers).text
        except:
            time.sleep(15)
        else:
            break
    soup = BeautifulSoup(source, 'html.parser')
    items = soup.find_all('div',attrs={'class':'kt-post-card__body'})

    counter = 0
    for item in items:
        counter += 1
        if item.text.find("توافقی") == -1 and item.text.find("نمایش") == -1:
            for i in item:
                link = i.parent.parent.parent.get('href').split('/')[3]
                idset.add(str(link))
                break
    return list(idset)

def car_info_from_page(page):
    url = "https://divar.ir/v/"+page.strip()
    # print(page)
    headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    while True:
        try:
            source = requests.get(url, headers=headers).text
        except:
            time.sleep(15)
        else:
            break
    soup = BeautifulSoup(source, 'html.parser')
    
    if len(soup.find_all('div', attrs={'class':'not-found-message'})) > 0:
        # print("Not Found")
        return
    car = {'page':page.strip()}
    
    if soup.find('a', attrs={'class':'kt-unexpandable-row__action'}) is None:
        # print("Not a car")
        return
    items = soup.find_all('a', attrs={'class':'kt-unexpandable-row__action'})[-1].get('href').split('/')
    if len(items) == 7:
        car['brand'] = items[4]
        car['model'] = items[5]
        car['type'] = items[6]
    elif len(items) == 6:
        car['brand'] = items[4]
        car['model'] = items[5]
        car['type'] = ""
    else:
        car['brand'] = items[4]
        car['model'] = ""
        car['type'] = ""
    items = soup.find_all('span',attrs={'class':'kt-group-row-item__value'})

    km = int(digits.fa_to_en(items[0].get_text()).replace("٬",""))
    if km < 1000:
        km *= 1000
    car['km'] = km
    yearTemp = digits.fa_to_en(items[1].get_text())
    intPart = re.findall(r'(\d+)', yearTemp)[0]
    if int(intPart) > 1900:
        car['year'] = int(intPart)
    else:
        car['year'] = JalaliDate(int(digits.fa_to_en(intPart)),1,1).to_gregorian().strftime("%Y")
    colors = ['آبی', 'آلبالویی', 'اطلسی', 'بادمجانی', 'برنز', 'بنفش', 'بژ', 'تیتانیوم', 'خاکستری', 'خاکی', 'دلفینی', 'ذغالی', 'زرد', 'زرشکی', 'زیتونی', 'سبز', 'سربی', 'سرمه\u200cای', 'سفید', 'سفید صدفی', 'طلایی', 'طوسی', 'عدسی', 'عنابی', 'قرمز', 'قهوه\u200cای', 'مسی', 'مشکی', 'موکا', 'نارنجی', 'نقرآبی', 'نقره\u200cای', 'نوک\u200cمدادی', 'پوست\u200cپیازی', 'کربن\u200cبلک', 'کرم', 'گیلاسی', 'یشمی']
    car['color'] = colors.index(items[2].get_text())
    items = soup.find_all('p', attrs={'class':'kt-unexpandable-row__value'})
    # print(len(items))
    itemlen = len(items)
    
    priceTemp = digits.fa_to_en(items[itemlen -1].get_text()).replace("٬","").replace("تومان","")
    intPart = re.findall(r'(\d+)', priceTemp)
    if len(intPart) == 0:
        # print("No Price")
        return
    car['price'] = int(priceTemp)
    motor_items = ['سالم', 'نیاز به تعمیر', 'تعویض شده']

    chassis_items = ['سالم و پلمپ', 'عقب ضربه\u200cخورده', 'عقب رنگ\u200cشده', 'جلو ضربه\u200cخورده', 'جلو رنگ\u200cشده', 'عقب ضربه\u200cخورده، جلو رنگ\u200cشده', 'عقب رنگ\u200cشده، جلو ضربه\u200cخورده', 'هردو ضربه\u200cخورده', 'هردو رنگ\u200cشده', 'ضربه\u200cخورده', 'رنگ\u200c']
    color_status_items = ['سالم و بی\u200cخط و خش', 'خط و خش جزیی', 'صافکاری بی\u200cرنگ', 'رنگ\u200cشدگی', 'دوررنگ', 'تمام\u200cرنگ', 'تصادفی', 'اوراقی']
    insurance_item = ['۱ ماه', '۲ ماه', '۳ ماه', '۴ ماه', '۵ ماه', '۶ ماه', '۷ ماه', '۸ ماه', '۹ ماه', '۱۰ ماه', '۱۱ ماه', '۱۲ ماه']
    gear_items = ['دنده\u200cای', 'اتوماتیک']
    car['chassis']= -1
    car['body'] = -1
    car['insurance']  = -1
    car['gear']  = -1
    car['motor'] = -1
    counter = 0
    for item in range(0, itemlen-1):
        # print(items[counter].get_text())
        if items[counter].get_text() in chassis_items:
            car['chassis'] = chassis_items.index(items[counter].get_text())
        elif items[counter].get_text() in color_status_items:
            car['body'] = color_status_items.index(items[counter].get_text())
        elif items[counter].get_text() in insurance_item:
            car['insurance'] = insurance_item.index(items[counter].get_text())
        elif items[counter].get_text() in gear_items:
            car['gear'] = gear_items.index(items[counter].get_text())
        elif items[counter].get_text() in motor_items:
            car['motor'] = motor_items.index(items[counter].get_text())
        counter += 1
    return car

def save_car_to_db(car, city, conn):
    cursor = conn.cursor()
    query = "INSERT INTO `cars` (`id`, `page`, `city`, `brand`, `model`, `type`, `km`, `year`, `color`, `motor`, `price`, `chassis`, `body`, `insurance`, `gear`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update page=page;"
    values = (car['page'], city, car['brand'], car['model'], car['type'], car['km'], car['year'], car['color'], car['motor'], car['price'], car['chassis'], car['body'], car['insurance'], car['gear'])
    cursor.execute(query, values)
    conn.commit()
def skip_registered_page(page):
    cursor = conn.cursor()
    query = "SELECT count(*) as pagecount FROM `cars` WHERE `page` = \"" + page +"\""
    cursor.execute(query)
    result = cursor.fetchone()
    if result[0] == 1:
        return True
    else:
        return False

conn = mysql.connector.connect(host="localhost", user="root", password="", database="maktabkhooneh")
cities = ["mashhad", "bojnurd", "ahvaz", "zanjan"
, "semnan", "zahedan", "shiraz", "qazvin", "qom", "sanandaj", "kerman"
, "kermanshah", "yasuj", "gorgan", "rasht", "khorramabad", "sari", "arak"
, "bandar-abbas", "hamedan", "yazd", "isfahan","tehran", "tabriz","urmia", "ardabil","karaj","ilam"
, "bushehr", "shahrekord", "birjand"]
while True:
    for city in cities:
        registered = False
        counter = 0
        for i in range(1, 50):
            if registered:
                break
            pages = grab_from_home_page(city, i)
            for page in pages:
                if skip_registered_page(page):
                    counter += 1
                    if counter == 5:
                        registered = True
                        break
                    else:
                        continue
                else:
                    counter = 0   
                car = car_info_from_page(page)
                if car is None:
                    print(page, "404")
                    time.sleep(2)
                else:
                    print(car)
                    save_car_to_db(car, city, conn)
                    time.sleep(2)
# print(skip_registered_page('wY_JQeGP'))
#SELECT brand, model, city, count(brand) as cc FROM `cars` GROUP BY brand, model, city ORDER BY cc DESC; 
#SELECT city, count(city) as cc FROM `cars` GROUP BY city ORDER BY cc DESC;
