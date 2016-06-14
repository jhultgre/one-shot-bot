from boop_generator import get_boop
import numberutilites as num_utils
import os

episodes= []
names = {}

with open('test_files/critical-success-episodes') as f:
    for line in f.readlines():
        line =line.strip()
        number = line.split(' ', 1)[0][:-1]
        # print line
        # print number
        episodes.append(number)
        names[number] = line

# print episodes
# print names
os.chdir('../core/')
os.system('pwd')
for i, number in enumerate(episodes):
    # print i, number
    with open('../one-shot-bot/templates/critical-success.template') as f:
        title = names[number]

        prev_episode = '[[Critical Success %s|%s]]' % (episodes[i-1], names[episodes[i-1]]) if i > 0 else 'N/A'
        # print prev_episode
        try:
            next_episode = '[[Critical Success %s|%s]]' % (episodes[i+1], names[episodes[i+1]])
        except Exception, e:
            next_episode = '[[Critical Success %s]]' % (int(episodes[i])+1)
        # print next_episode
        template = f.read()
        template = template.replace('$title', title).replace('$prev', prev_episode).replace('$next',next_episode)
        # print template
        os.system('python pwb.py add_text -page:"Critical Success '+episodes[i]+'" -text:"'+template+'" -up -except:"\{\{([Tt]emplate:|)[Cc]ritical[Ss]uccess[Ee]pisode" -always -summary:"'+get_boop()+' edit made by a droid"')
