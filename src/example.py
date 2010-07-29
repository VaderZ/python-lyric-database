# -*- coding: utf-8 -*-

from pylyrdb import Lyric

#Create an instance of the lyric database connector which uses the sqlite db for caching
lyric  = Lyric("sql")
#To use the xml file for caching create object as follows lyric  = Lyric("xml")
#To disable caching create object as follows lyric  = Lyric(None)

# Get the lyric
lyric_data = lyric(u"Iced Earth", u"When The Eagle Cries")
# lyric_data is a dictionary with the following data 
#{"author":<song author>, "track": <song title>, "text": <song text>}

# Print the lyric
print lyric

# Delete the lyric from cache
lyric_data = lyric.delete(u"Iced Earth", u"When The Eagle Cries")


