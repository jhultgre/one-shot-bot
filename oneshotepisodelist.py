import numberutilites as num_utils



with open('test_files/one-shot-episodes') as f:
    with open('../core/userfiles/one-shot-links','w') as out:
        episode = 1
        extra = 1
        bonus = 1
        for line in f.readlines():
            name = line.strip()
            title = name.split(':')[1].strip()

            if 'Extra' in name:
                out.write('[[One Shot Extra %s]]\n' % num_utils.number_to_text(extra))
                out.write('[[Episode Extra {0}|One Shot Extra {0}: {1}]]\n'.format(extra, title))
                
                out.write('[[One Shot Extra %s|\n' % num_utils.number_to_text(extra))
                out.write('[[Episode Extra {0}|\n'.format(extra))
                
                out.write('[[One Shot Extra %s]]\n' % extra)
                out.write('[[Episode Extra {0}|One Shot Extra {0}: {1}]]\n'.format(extra, title))
                
                out.write('[[Episode Extra %s]]\n' % extra)
                out.write('[[Episode Extra {0}|One Shot Extra {0}: {1}]]\n'.format(extra, title))
                
                extra += 1
            elif 'BONUS' in name:
                out.write('[[One Shot BONUS %s]]\n' % num_utils.number_to_text(bonus))
                out.write('[[Episode BONUS {0}|One Shot BONUS {0}: {1}]]\n'.format(bonus, title))
                
                out.write('[[One Shot BONUS %s|\n' % num_utils.number_to_text(bonus))
                out.write('[[Episode BONUS {0}|\n'.format(bonus))
                
                out.write('[[One Shot BONUS %s]]\n' % bonus)
                out.write('[[Episode BONUS {0}|One Shot BONUS {0}: {1}]]\n'.format(bonus, title))
                
                out.write('[[Episode BONUS %s]]\n' % bonus)
                out.write('[[Episode BONUS {0}|One Shot BONUS {0}: {1}]]\n'.format(bonus, title))
                bonus += 1
            else:
                out.write('[[Episode %s]]\n' % num_utils.number_to_text(episode))
                out.write('[[Episode {0}|One Shot Episode {0}: {1}]]\n'.format(episode, title))
                
                out.write('[[Episode %s|\n' % num_utils.number_to_text(episode))
                out.write('[[Episode {0}|\n'.format(episode))
                
                out.write('[[Episode %s]]\n' % episode)
                out.write('[[Episode {0}|One Shot Episode {0}: {1}]]\n'.format(episode, title))
                
                episode += 1