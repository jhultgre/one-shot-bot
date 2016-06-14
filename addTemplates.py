import os
from boop_generator import get_boop
# from os import listdir
# from os.path import isfile, join
# onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
files = os.listdir('../core/userfiles/episodes/')
print get_boop()

os.chdir('../core/')
os.system('pwd')
for f in files:
    print f
    # print 'python pwb.py add_text -page:"'+f+'" -up -except:{{CampaignEpisode -simulate -textfile:"userfiles/episodes/'+f+'"'
    # os.system('python pwb.py add_text -page:"Campaign:'+f+'" -up -except:"\{\{([Tt]emplate:|)[Cc]ampaign[Ee]pisode" -always -summary:"'+get_boop()+' this edit was made by a droid" -textfile:"userfiles/episodes/'+f+'"')
