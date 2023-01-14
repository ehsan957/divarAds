import csv
import mysql.connector


conn = mysql.connector.connect(host="localhost", user="root", password="", database="maktabkhooneh")
cursor = conn.cursor()
chassis_items = ['سالم و پلمپ', 'عقب ضربه\u200cخورده', 'عقب رنگ\u200cشده', 'جلو ضربه\u200cخورده', 'جلو رنگ\u200cشده', 'عقب ضربه\u200cخورده، جلو رنگ\u200cشده', 'عقب رنگ\u200cشده، جلو ضربه\u200cخورده', 'هردو ضربه\u200cخورده', 'هردو رنگ\u200cشده', 'ضربه\u200cخورده', 'رنگ\u200c']
color_status_items = ['سالم و بی\u200cخط و خش', 'خط و خش جزیی', 'صافکاری بی\u200cرنگ', 'رنگ\u200cشدگی', 'دوررنگ', 'تمام\u200cرنگ', 'تصادفی', 'اوراقی']
insurance_item = ['۱ ماه', '۲ ماه', '۳ ماه', '۴ ماه', '۵ ماه', '۶ ماه', '۷ ماه', '۸ ماه', '۹ ماه', '۱۰ ماه', '۱۱ ماه', '۱۲ ماه']
gear_items = ['دنده\u200cای', 'اتوماتیک']
colors = ['آبی', 'آلبالویی', 'اطلسی', 'بادمجانی', 'برنز', 'بنفش', 'بژ', 'تیتانیوم', 'خاکستری', 'خاکی', 'دلفینی', 'ذغالی', 'زرد', 'زرشکی', 'زیتونی', 'سبز', 'سربی', 'سرمه\u200cای', 'سفید', 'سفید صدفی', 'طلایی', 'طوسی', 'عدسی', 'عنابی', 'قرمز', 'قهوه\u200cای', 'مسی', 'مشکی', 'موکا', 'نارنجی', 'نقرآبی', 'نقره\u200cای', 'نوک\u200cمدادی', 'پوست\u200cپیازی', 'کربن\u200cبلک', 'کرم', 'گیلاسی', 'یشمی']
motor_items = ['سالم', 'نیاز به تعمیر', 'تعویض شده']


with open('Cars.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Brand', 'Model', 'Tip', 'Gear', 'KM', 'Year', 'Color', 'Body', 'Motor', 'Chassis', 'Price', 'City', 'Page', 'Date']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    query = "SELECT * FROM `cars`"
    cursor.execute(query)
    results = cursor.fetchall()
    for result in  results:
        writer.writerow({'Brand': result[3], 'Model': result[4], 'Tip': result[5], 'Gear': gear_items[int(result[14])], 'KM': result[6], 'Year': result[7],'Color': colors[int(result[8])], 'Body': color_status_items[int(result[12])] if int(result[12]) != -1 else "", 'Motor': motor_items[int(result[9])] if int(result[9]) != -1 else "", 'Chassis': chassis_items[int(result[11])] if int(result[11]) != -1 else "", 'Price': result[10],'City': result[2] ,'Page': "http://divar.ir/v/"+result[1]+" ", 'Date': result[15]})
    
    