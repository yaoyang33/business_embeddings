import optparse
import sys
import json
import pandas as pd
import os
from nltk.tokenize import word_tokenize



def flatten(l):
    return [item for sublist in l for item in sublist]

def get_business_tags(j):
    '''
    Get attribute tags from BUSINESS json object
    :param j: json object
    :return: business and
    '''
    business = j['business_id']
    # print('category is:{}'.format(j['categories']))
    cats = get_business_cats(j)
    # print('cat done')
    city = [j['city'].lower()]
    state = [j['state'].lower()]
    stars = ['stars.'+str(j['stars'])]
    # print('attribute is:{}'.format(j['attributes']))
    onelevelatts = [k for k,v in j['attributes'].items() if type(k) != dict] if j['attributes'] is not None else []
    twolevelatts = [k for k,v in j['attributes'].items() if type(v)==dict] if j['attributes'] is not None else []
    atts = ['_'.join((k+'.'+str(v)).lower().split()) for k,v in j['attributes'].items() if k in onelevelatts] if j['attributes'] is not None else []
    atts += flatten([['_'.join('.'.join([a,k,str(v)]).lower().split()) for k,v in j['attributes'][a].items()] for a in twolevelatts]) if j['attributes'] is not None else ''
    # print('done')
    return business, cats, cats+city+state+stars+atts

def get_business_cats(j):
    '''
    Get categories
    :param j:
    :return:
    '''
    cats = [''.join(('cat.'+ ct.lower()).split()) for ct in j['categories'].split(",")]  if  j['categories'] is not None else []
    return cats

if __name__=="__main__":


    ## Get command line arguments
    optparser = optparse.OptionParser()
    optparser.add_option("-D", "--dirname", type='string', dest='dirname', default='../data', help='Path to directory containing yelp data')
    # optparser.add_option("-W", "--wordvocabfile", type='string', dest='wordvocabfile', default='../data/processed/vocab_count', help='Path to vocab count file')
    # optparser.add_option("-V", "--tagvocabfile", type='string', dest='tagvocabfile', default='../data/processed/tag_vocab_count')
    # optparser.add_option("-T", "--thr", type='int', dest='THR', default=50, help='Threshold for considering tokens/contexts')
    (opts, _) = optparser.parse_args()

    sys.stderr.write('Reading business attributes...')
    busfile = '../data/business.json'
    businesses = {}
    with open(busfile,'r') as fin:
        # head = [next(fin) for x in range(100)]
        for line in fin:
            j = json.loads(line)
            # print('start by {}'.format(j))
            bid, cats, atts = get_business_tags(j)
            businesses[bid] = [a for a in atts]
            # print(businesses)
    sys.stderr.write('Number of businesses %d\n' % len(businesses))

    filelist = [os.path.join(opts.dirname, f) for f in os.listdir(opts.dirname) if 'review' in f or 'tip' in f]
    print(filelist)
    i = 0
    for f in filelist:
        with open(f,'rU') as fin:
            head = [next(fin) for x in range(100)]
            for line in fin:
                sample = json.loads(line)
                bid = sample['business_id']
                text = sample['text']
                toks = [t for t in word_tokenize(text.lower())]

                for t in toks:
                    print (bid, t)
                for a in businesses[bid]:  # repeat for every tip/review
                    print (bid, a)

                i += 1
                if i % 10000 == 0:
                    sys.stderr.write('.')
