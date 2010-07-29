# -*- coding: utf-8 -*-

import urllib
import os, sys, re
from xml.etree import ElementTree
import sqlite3

class Lyric(object):
    """Module to work with the lyrics from http://lyrics.mirkforce.net"""
    def __init__(self, cache_type = "sql"):
        self.cache_type = cache_type
        self.xml_cache_file = os.path.join(sys.path[0],"cache.xml")
        self.sql_cache_file = os.path.join(sys.path[0],"cache.db")
        self.artist = None
        self.track = None
        self.text = None
                
    def _lyric_retrive(self, artist, track):
        url = "http://lyrics.mirkforce.net/cgi-bin/lepserver.cgi?%s"
        request = '<?xml version="1.0"?>\
                   <query agent="pylyrdb" version="1.0">\
                       <song id="0" artist="%s" title="%s"/>\
                   </query>'\
                    % (artist.encode("utf-8"), track.encode("utf-8"))
        lyric_dom = ElementTree.parse(urllib.urlopen(url % request))
        if lyric_dom.getroot().find("song") is None:
            return
        else:
            return (lyric_dom.getroot().find("song").find("text").text).encode('utf8')
       
    def _cache_open(self):
        if not self.cache_type:
            return
        elif self.cache_type == "xml":
            try:
                xml = ElementTree.parse(self.xml_cache_file)
            except IOError:
                temp = ElementTree.ElementTree(ElementTree.Element("lyrics"))
                temp.write(self.xml_cache_file, "utf-8")
                xml = ElementTree.parse(self.xml_cache_file)
            return xml
        elif self.cache_type == "sql":
            connection = sqlite3.connect(self.sql_cache_file)
            cursor = connection.cursor()
            cursor.execute("""select name from sqlite_master where name = "lyrics" """)
            if not cursor.fetchall():
                cursor.execute("""create table lyrics
                                (hash text unique, artist text, track text, text text)""")
                connection.commit()
            return connection, cursor
                
    def _cache_update(self, artist, track, text):
        if not self.cache_type:
            return
        elif text is None:
            return
        elif self.cache_type == "xml":
            xml = self._cache_open()
            root = xml.getroot()
            ElementTree.SubElement(root, self._hash_calc(artist, track), artist = artist, track = track)\
                                    .text = text
            xml.write(self.xml_cache_file, "utf-8")
        elif self.cache_type == "sql":
            connection, cursor = self._cache_open()
            cursor.execute("""insert into lyrics 
                        values ("%s","%s","%s","%s")"""\
                        %(self._hash_calc(artist, track), artist.replace('"','""'),\
                         track.replace('"','""'), text.replace('"','""')))
            connection.commit()
            cursor.close()
            connection.close()
            
    def _cache_retrive(self, artist, track):
        if not self.cache_type:
            return
        if self.cache_type == "xml":
            xml = self._cache_open()
            root = xml.getroot()
            if root.find(self._hash_calc(artist, track)) is None:
                return
            else:
                return root.find(self._hash_calc(artist, track)).text
        if self.cache_type == "sql":
            connection, cursor = self._cache_open()
            cursor.execute("""select text from lyrics where hash = "%s" """\
                            % self._hash_calc(artist, track))          
            text = cursor.fetchone()
            cursor.close()
            connection.close()
            if text:
                return text[0]
            else:
                return
        
    def _hash_calc(self, artist, track):
        return "".join(re.findall("\w","".join([artist,track]).lower(), re.UNICODE)).replace("_","")
    
    def _cache_delete(self, artist, track):
        if not self.cache_type:
            return
        elif self.cache_type == "xml":
            xml = self._cache_open()
            root = xml.getroot()
            try:
                root.remove(root.find(self._hash_calc(artist, track)))
            except AssertionError:
                pass
            xml.write(self.xml_cache_file,"utf-8")
        elif self.cache_type == "sql":
            connection, cursor = self._cache_open()
            cursor.execute("""delete from lyrics where hash = "%s" """\
                           % self._hash_calc(artist, track))
            connection.commit()
            cursor.close()
            connection.close()
    
    def __str__(self):
        temp = ["Artist: ", self.artist, "\n\n", "Track: ", self.track, "\n\n", self.text]
        return "".join(temp)
    
    def __call__(self, artist, track):
        """Get the lyric"""
        self.artist = artist
        self.track = track
        if not self.cache_type:
            self.text = self._lyric_retrive(artist, track)
        text = self._cache_retrive(self.artist, self.track)
        if text:
            self.text = text
        else:
            self.text = self._lyric_retrive(self.artist, self.track)
            self._cache_update(self.artist, self.track, self.text)
        return {"artist":self.artist, "track":self.track, "text": self.text}
    
    def delete(self, artist, track):
        """Delete cached lyric"""
        self._cache_delete(artist, track)