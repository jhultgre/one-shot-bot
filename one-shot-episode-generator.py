import numberutilites as num_utils

with open('../core/userfiles/one-shot-episodes','w') as f:
    for i in xrange(1,127):
        f.write('[[Episode %s]]\n' % num_utils.number_to_text(i))
        f.write('[[Episode %s]]\n' % i)
    for i in xrange(1,7):
        #extra
        f.write('[[One Shot Extra %s]]\n' % num_utils.number_to_text(i))
        f.write('[[Episode Extra %s]]\n' % i)
    for i in xrange(1,6):
        #bonus
        f.write('[[One Shot BONUS Episode %s]]\n' % num_utils.number_to_text(i))
        f.write('[[Episode BONUS %s]]\n' % i)