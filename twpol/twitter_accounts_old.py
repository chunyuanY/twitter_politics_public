import time

class TwitterAccount:
    def __init__(self, consumer_key, consumer_secret, my_key, my_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.my_key = my_key
        self.my_secret = my_secret
        self.available = time.time()
        self.stalled = False
    def setAvailable(self, when):
        self.available = when

TWITTER_ACCOUNTS = [

    TwitterAccount(
        consumer_key = '8KUqX5jvpDIjqp1B1nzag',
        consumer_secret = '02NdFzcuqDeauSmBbCUNTKBTN0Nb0hpNA4tBqfvt7E',
        my_key = '1461327583-PZLqeByUNONj17TfL0tbegR6Bnkc51RskBS5Yzh',
        my_secret = 'FghDwTkWMmHtb2H56SrTpFXLjYfRaCRpm6bxXpqNh8'
    ),
    TwitterAccount(
        consumer_key = 'jeNt6VwXYSlzvEIbRGn9HQ',
        consumer_secret = 'h18TRupR4rYPuDV1EU0evlKM3I7cT6rcqoDaVyw94',
        my_key = '1461283332-BEC3CE32A59B5Vlq2eyAN2uZNwEL6El1nKEslM8',
        my_secret = 'VedlcKsnSkCBc9EzKqo2IlEJzItkcrISgO4M9fU3U'
    ),
    TwitterAccount(
        consumer_key = 'gcLSLc1JwrmGNFR7TOqJA',
        consumer_secret = 'enOiImRrgtmYHA0l1eOkjuIcxwAAWeRpHFUm19dTma0',
        my_key = '1461303614-u8isV6E4fUnrL2VmTlZmPueochbiEnONvhtfzna',
        my_secret = '2j4GsdsmvqoZuuvP61oAEhhpDMsBNPlHCtM8s6XNFyM'
    ),
   TwitterAccount(
        consumer_key = 'v2dpRzMZqQ109ymVJIrQ5w',
        consumer_secret = 'U4w8TRIUuflLSM3a9toGCqnJTNKQbssPAQ38Mn5zQ',
        my_key = '1461315277-F96cHP53t33gUIlxoFSmJbBOgYIXYsiWq0aDGRH',
        my_secret = '1jAoievDapwNDbzV8f0Q3whtvAPJhnCuDYMVkz2Tc'
    ),
    TwitterAccount(
        consumer_key = '8mRKKPECVmf0myfbjfnMg',
        consumer_secret = 'tWdU4SDks5uXv5tnLd1NOBQ4f8OuuUKAVg8ofcp7xeY',
        my_key = '1461296480-a5MHiiuasWidiuJuoxyBbjm0v1vF4RRDpi2Qd4s',
        my_secret = 'o65z02NBc6bBUGRc2CTDtLtjilNif5cOaBRFI3AyE'
    ),
    TwitterAccount(
        consumer_key = 'BvhQJW5N34LSVmeskBbqyA',
        consumer_secret = 'zLfqOf5SBiHqUp66l8tt8xNU2hx14QowkYNODIFj2Q',
        my_key = '1457639706-Shx14dcUozi8lY2fKeSHNbu5mNepRsbc8kNpkw4',
        my_secret = '0OWQYYMUqEsCR4ZNxoVDAmPZ7aeuKpAQF50MOP7ZTg'
    ),
    TwitterAccount(
        consumer_key = 'DK1MowmC4ePuoKXfGmA',
        consumer_secret = 'jYhmBJNrhc7zJWqOZwpeLpfn2nfMOnBZxmvNNmkWFA',
        my_key = '1457642875-DftHOYwmVEAKOQyyFNzNQiIq567hI626RQmrdcu',
        my_secret = 'V9slRi3GzV5xxNLSLeim0rkxPsUkpQjQKGlvrdSqY'
    ),
    TwitterAccount(
        consumer_key = 'Jt1AqeIILP7Rec9NQtfQ',
        consumer_secret = '6GukCBbiAIZkun6bi58X7bGruXQWtJ3wElLFh6DtKs',
        my_key = '1455219841-R9ZOfOVUcfcNhT52lQ1tRmC9DffXUdq8ikvhST2',
        my_secret = 'T9NakQEbKeexpKoHaIVJYyklANld8wXtfCxPfE2yCQ'
    ),
    TwitterAccount(
        consumer_key = 'JHb7101jJgeLcfXXaJVSA',
        consumer_secret = 'fplQmqEsp1CSu7viEVsASBgOrOmHJhWPrF1NqPWww',
        my_key = '582858030-h58sX55OJFiVsMQo0BibwI2S7Bz8Wflw2w4kvvdg',
        my_secret = 'bcrtY8MsOYg6bSb7aJ2qH38x0TU9HWnOzJ6XWfwkm8'
    ),
    TwitterAccount(
        consumer_key = '2uzwkV5dYHWSBcT3kz0qw',
        consumer_secret = '4hTFosoun7RjphqyTtPmy6AS6C1fk1SLekR3XfqWdJ4',
        my_key = '1452509881-G6rmlNAmALP5kgoBX5kKZHnpXN2AbVVq7Z2jffM',
        my_secret = '4UPZG8Ro8xDydQMTFjC4KxhIzYPHVTmFBPavh1egQ'
    ),
    TwitterAccount(
        consumer_key = 'ftOlR6C6ayuB7vPqx3pBwA',
        consumer_secret = 'Pv4wLot3sknQoh2iA5voxJDDzQr0C25KoRWhZI',
        my_key = '1355804516-NAGH3Z2g9uL7iGqfp4siuE5OfEgYHjk2ODj0KIg',
        my_secret = 'MG0eUwIhV9kfx2rPk3znCnrDntZzd6n39OLNVkHM05c'
    ),
    TwitterAccount(
        consumer_key = 'rYZOcXQaoWrLwNSNxmC6sA',
        consumer_secret = 'IilimQExeiwM2AnRVGl4B6QdoB4mz9JcXhSq63rig',
        my_key = '1442984695-z3qfO7bYvVCoC7L3dtxhRgiaLJnHgM8STPFCWOI',
        my_secret = 'C6IUOD8Xb62vkhe6RlvtsAvdZIeotQgfWcKusc'
    )

]

def initializeCredentials():
    import simplejson
    f = open('twitter_credentials.json', 'w')
    to_write = []
    for x in TWITTER_ACCOUNTS:
        cred = {
            'consumer_key': x.consumer_key,
            'consumer_secret': x.consumer_secret,
            'my_key':x.my_key,
            'my_secret':x.my_secret
        }
        to_write.append(cred)
    json = simplejson.dumps(to_write)
    f.write(json)
    f.close()