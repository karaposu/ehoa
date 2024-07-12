# i am creating an app which can take bank document of monthly spendings and then turn it into
#a analyis.  i need 3 main componentns.

#  a code to extract a table from a pdf in pandas format.
#  a code to process string fields in this dataframe with following rules for further analysis
#  a code to show results in a pie graph.

#

# raw df have these column  "Tarih",  "Açıklama",  "Tutar",  "Bakiye"
#tarih shows the date of the spending
#Açıklama is description of the spending and it contains a couple of important information such as
## -is spending done by card or it was a transfer.
## -how much is spend and in what currency
## -payment is done to where
## -if payment is done in another currency, it show exchange rate

## these are all valuable information which will help us refine it further.

## Tutar is how much is spent.


'''

i want to extract featuers from Açıklama column. Açıklama description  can be one of the following class:


coffea, grocories, restaurant, , taxi, bus, akpil. plane tickets, havaist, subscriptions, clothes, bills, other items,

food, accomondation, money transfers, transportation, cash withdral, subscriptions, all_other_payments

and i want to categorize food into these

grocories, restaurant,

accomondation can be airbnb, rent, booking, hotels.com

transportation can be
taxi, bus, akpil. plane tickets, havaist etc

subscriptions include all subscriptions.

all_other_payments


i want to
'''


categories = {
    'coffea': ['KAFE', 'KOFEYNYA', 'Cinnabon'],
    'groceries': ['Gipermarket', 'SHOP', 'I.-SHOP', 'GROCERIES'],
    'restaurant': ['Restoran', 'CHAYHONA', 'GRAND CAFE', 'BURGER KING'],
    'taxi': ['YANDEX.GO'],
    'bus': ['HAVAIST', 'SBUX'],
    'plane tickets': ['Kurban'],
    'subscriptions': ['Spotify', 'DIGITALOCEAN', 'APPLE.COM', 'FIGMA', 'Google Tandem App', 'OPENAI', 'CTRLF.PLUS'],
    'clothes': ['SHOP "SOKOLOV"'],
    'other items':" " }



