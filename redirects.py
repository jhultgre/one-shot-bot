import wikiatools
import numberutilites as num_utils

eps = '''  10 Episode Eight
  11 Episode Eighteen
  12 Episode Eleven
  13 Episode Fifteen
  14 Episode Fifty
  15 Episode Fifty Five
  16 Episode Fifty Four
  17 Episode Fifty One
  18 Episode Fifty Six
  19 Episode Fifty Three
  20 Episode Fifty Two
  21 Episode Five
  22 Episode Forty
  23 Episode Forty Eight
  24 Episode Forty Five
  25 Episode Forty Four
  26 Episode Forty Nine
  27 Episode Forty One
  28 Episode Forty Seven
  29 Episode Forty Six
  30 Episode Forty Three
  31 Episode Forty Two
  32 Episode Four
  33 Episode Fourteen
  34 Episode Nine
  35 Episode Nineteen
  36 Episode One
  37 Episode Seven
  38 Episode Seventeen
  39 Episode Six
  40 Episode Sixteen
  41 Episode Ten
  42 Episode Thirteen
  43 Episode Thirty
  44 Episode Thirty Eight
  45 Episode Thirty Five
  46 Episode Thirty Four
  47 Episode Thirty Nine
  48 Episode Thirty One
  49 Episode Thirty Seven
  50 Episode Thirty Six
  51 Episode Thirty Three
  52 Episode Thirty Two
  53 Episode Three
  54 Episode Twelve
  55 Episode Twenty
  56 Episode Twenty Eight
  57 Episode Twenty Five
  58 Episode Twenty Four
  59 Episode Twenty Nine
  60 Episode Twenty One
  61 Episode Twenty Seven
  62 Episode Twenty Six
  63 Episode Twenty Three
  64 Episode Twenty Two
  65 Episode Two
  66 Flashback Episode Eight
  67 Flashback Episode Five
  68 Flashback Episode Four
  69 Flashback Episode Nine
  70 Flashback Episode One
  71 Flashback Episode Seven
  72 Flashback Episode Six
  73 Flashback Episode Ten
  74 Flashback Episode Three
  75 Flashback Episode Two
  77 Sidequest Episode Four
  78 Sidequest Episode One
  79 Sidequest Episode Three
  80 Sidequest Episode Two'''

eps = eps.split('\n')
eps = [x[5:]for x in eps]
print eps
numbers = [num_utils.text_to_number(x.split('Episode ')[1]) for x in eps]
print numbers

wikiatools.clear_new_pages()

for ep in eps:
    number = num_utils.text_to_number(ep.split('Episode ')[1])
    title = ep.split('Episode ')[0] + 'Episode ' + str(number)
    print ep , number, title
    wikiatools.write_page('Campaign:%s' % title, '#REDIRECT [[Campaign:%s]]'% ep)

wikiatools.post_pages()