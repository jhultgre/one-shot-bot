import numberutilites as num_utils

clean_template = None
with open('templates/campaign.template') as f:
    clean_template = f.read()

for i in xrange(2, 51):
    title = 'Episode '+num_utils.number_to_text(i)
    next = 'Episode '+num_utils.number_to_text(i+1)
    prev = 'Episode '+num_utils.number_to_text(i-1)

    template = clean_template

    template = template.replace('$title',title).replace('$next', next).replace('$prev', prev)
    with open('../core/userfiles/episodes/' + title,'w') as f:
        f.write(template)