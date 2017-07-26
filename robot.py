from textblob import TextBlob
from readability.readability import Document
import urllib.request
from translation import bing
from bs4 import BeautifulSoup
import requests
import re
from pytrends.request import TrendReq
import tweepy

#INPUT AND DIVIDE WORDS
z = input("WHAT ARE YOU LOOKING FOR?\n")


if len(z.split()) == 1:
    url = ('https://www.google.com.mx/search?q=%s&source=lnms&tbm=nws&sa=X&ved=0ahUKEwiJz8CEsKjUAhWg3oMKHboXA3gQ_AUIDSgE&biw=1532&bih=782') % (z)
elif len(z.split()) == 2:
    url = ('https://www.google.com.mx/search?q=%s+%s&&source=lnms&tbm=nws&sa=X&ved=0ahUKEwiJz8CEsKjUAhWg3oMKHboXA3gQ_AUIDSgE&biw=1532&bih=782') % (z.split()[0],z.split()[1])
elif len(z.split()) == 3:
    url = ('https://www.google.com.mx/search?q=%s+%s+%s&source=lnms&tbm=nws&sa=X&ved=0ahUKEwiJz8CEsKjUAhWg3oMKHboXA3gQ_AUIDSgE&biw=1532&bih=782') % (z.split()[0],z.split()[1],z.split()[2])
elif len(z.split()) == 4:
    url = ('https://www.google.com.mx/search?q=%s+%s+%s+%s&source=lnms&tbm=nws&sa=X&ved=0ahUKEwiJz8CEsKjUAhWg3oMKHboXA3gQ_AUIDSgE&biw=1532&bih=782') % (z.split()[0],z.split()[1],z.split()[2],z.split()[3])
elif len(z.split()) == 5:
    url = ('https://www.google.com.mx/search?q=%s+%s+%s+%s+%s&source=lnms&tbm=nws&sa=X&ved=0ahUKEwiJz8CEsKjUAhWg3oMKHboXA3gQ_AUIDSgE&biw=1532&bih=782') % (z.split()[0],z.split()[1],z.split()[2],z.split()[3],z.split()[4])
else:
    print("Please use at least one word or five tops")


#IDENTIFY OURSELVES
browser = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':browser,}
#LINKS LIST
page = requests.get(url)
soup = BeautifulSoup(page.content, "lxml")
links = soup.findAll("a")

lista = []
l = []
a = []
num_articulos = 4


for link in  soup.find_all("a",href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
    l.append(re.split(":(?=http)",link["href"].replace("/url?q=",""))[0])
    for each in l:
        if requests.get(each).status_code == 200 and len(a) < num_articulos:
                print("Link # %s is %s" % (len(a), each))
                a.append(each)
                a = (list(set(a)))
        elif requests.get(each).status_code == 200 and len(a) == num_articulos:
            break
print("Links are ready\n")

for some in a:
    try:
        print("Loading...")
        request = urllib.request.Request(some, None, headers)
        response = urllib.request.urlopen(request)
        data = response.read()
        resumen = Document(data).summary()
        texto = str(resumen)
        traduccion = (bing(texto, dst='en'))
        analisis = TextBlob(traduccion)
        factor = ((analisis.polarity*5)+5) * (1 - analisis.subjectivity)
        lista.append(factor)
    except:
        pass
print("\nWhat Google News think about %s being 10 the best and 1 the worst is %s" % (z, sum(lista[:]) / len(lista[:])))




google_username = ""
google_password = ""
path = ""

pytrend = TrendReq(google_username, google_password, custom_useragent='')
pytrend.build_payload(kw_list=[z])

interest_over_time_df = pytrend.interest_over_time()
thirty = 30
sixty = 60
ninety = 90
oneeighty = 180
ten = 10

yesterday = interest_over_time_df.tail(ten)
last_30 = interest_over_time_df.tail(thirty)
last_60 = interest_over_time_df.tail(sixty)
last_90 = interest_over_time_df.tail(ninety)
last_180 = interest_over_time_df.tail(oneeighty)

print("Interest in %s based on Google Trends:" % z)

last_180 = last_180[z]
last_180 = last_180[last_180 > 0]
print("Last 180 days: %s" % last_180.mean())

last_90 = last_90[z]
last_90 = last_90[last_90 > 0]
print("Last 90 days: %s" % last_90.mean())

last_60 = last_60[z]
last_60 = last_60[last_60 > 0]
print("Last 60 days: %s" % last_60.mean())

last_30 = last_30[z]
last_30 = last_30[last_30 > 0]
print("Last 30 days: %s" % last_30.mean())

yesterday = yesterday[z]
yesterday = yesterday[yesterday > 0]
print("Last 10 days: %s " % yesterday.mean())


per_180 = (last_90.mean()-last_180.mean())/last_90.mean()
per_90 = (last_60.mean()-last_90.mean())/last_60.mean()
per_60 = (last_30.mean()-last_60.mean())/last_30.mean()
per30 = (yesterday.mean()-last_30.mean())/yesterday.mean()

print("Interest from 6 months has moved: %s%%\nInterest from 3 months has moved: %s%%\nInterest from 2 months has moved: %s%%\nInterest from last month has moved %s%%\n" % (round(per_180*100), round(per_90*100), round(per_60*100), round(per30*100)))




consumer_key = ''
consumer_secret = ''

access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

tweets = api.search(z)

lista = []

print("Tweets:\n")

for each in tweets:
    analisis = TextBlob(each.text)
    print(each.text, analisis.polarity, analisis.subjectivity)
    factor = ((analisis.polarity * 5) + 5) * (1 - analisis.subjectivity)
    lista.append(factor)

print("\nWhat Twitter thinks about %s being 10 the best and 1 the worst is %s" % (z, sum(lista[:]) / len(lista[:])))
