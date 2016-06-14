#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wikiatools
import sys
import codecs

reload(sys)  
sys.setdefaultencoding('utf8')
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

x = '''
<p><a href="http://www.sarahlynnebowman.com/" target="_blank">Sarah&#8217;s website </a><br />
<a href="http://www.livinggamesconference.com/" target="_blank">Living Games Conference </a><br />
<a href="http://www.drivethrurpg.com/product/102295/The-Functions-of-RolePlaying-Games-How-Participants-Create-Community-Solve-Problems-and-Explore-Identity?term=functions+of+role-playing" target="_blank">The Functions of Role-Playing Games </a><br />
<a href="http://www.vice.com/read/at-this-danish-school-larping-is-the-future-of-education-482" target="_blank">Østerskov Efterskole</a><br />
<a href="http://nordiclarp.org/wiki/Kapo" target="_blank">Kapo, the Danish Prison Larp</a><br />
<a href="http://shoshanakessock.com/2014/05/31/video-ethical-content-creation-and-the-freedom-to-create/" target="_blank">Shoshanna Kessok&#8217;s Nordic Larp Talk </a><br />
<a href="https://docs.google.com/document/d/1SB0jsx34bWHZWbnNIVVuMjhDkrdFGo1_hSC2BWPlI3A/edit" target="_blank">X-Card </a><br />
<a href="http://www.cowlarp.com/" target="_blank">College of Wizardry </a><br />
<a href="http://www.wyrdcon.com/2014/05/the-wyrd-con-companion-book/" target="_blank">Wyrd Con Companion Book</a><br />
<a href="http://leavingmundania.com/2015/08/04/your-larps-only-as-safe-as-its-safety-culture/" target="_blank">Trols Pedersen on Safety Culture</a><br />
<a href="http://www.dystopiarisinglarp.com/l1r7q9wo6h0oivhkhy7cioqdvmp688" target="_blank">Dystopia Rising</a><br />
<a href="http://leavingmundania.com/games/" target="_blank">This Miracle</a><br />
<a href="https://en.wikipedia.org/wiki/RuPaul%27s_Drag_Race" target="_blank">RuPaul&#8217;s Drag Race</a><br />
<a href="https://en.wikipedia.org/wiki/Persona_(psychology)" target="_blank">Jung&#8217;s &#8220;Personae&#8221; </a><br />
<a href="https://en.wikipedia.org/wiki/Erikson%27s_stages_of_psychosocial_development#Fidelity:_identity_vs._role_confusion_.28adolescence.2C_13.E2.80.9319_years.29" target="_blank">Erik Erikson&#8217;s &#8220;Ego Identity&#8221;</a><br />
<a href="http://analoggamestudies.org/" target="_blank">Analog Game Studies</a><br />
<a href="http://www.keithjohnstone.com/" target="_blank">Keith Johnstone&#8217;s Impro</a><br />
<a href="http://www.drivethrurpg.com/product/134196/Chuubos-Marvelous-WishGranting-Engine" target="_blank">Chuubo&#8217;s Marvellous Wish Granting Engine</a><br />
<a href="http://amtgard.com/" target="_blank">Amtgard</a><br />
<a href="http://www.cosmicjoke.co.uk/treasure-trapped/" target="_blank">Treasure Trapped</a><br />
<a href="http://www.prepareforplanetfall.com/#/" target="_blank">Planetfall</a><br />
<a href="https://www.mindseyesociety.org/" target="_blank">Mind&#8217;s Eye Society</a><br />
<a href="http://magischola.com/" target="_blank">New World Magischola</a><br />
<a href="https://en.wikipedia.org/wiki/Role_Models" target="_blank">Role Models</a><br />
<a href="http://www.knudepunkt.org/" target="_blank">&#8220;The Nordic Convention&#8221;</a><br />
<a href="http://www.fastaval.dk/?lang=en" target="_blank">Fastaval</a><br />
<a href="http://www.foolreversed.com/" target="_blank">Nordsplainer vs Amerijerk</a></p>
'''
print wikiatools.format_links(x)