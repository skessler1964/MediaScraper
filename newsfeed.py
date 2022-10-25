import json
import os
import webbrowser
import requests
import datetime
import traceback
import time

class Video:
    def __init__(self):
        self.description=None
        self.url=None
        self.icon=None
    
    def __init__(self, description, url):
        self.description=description
        self.url=url

    def __init__(self, description, url, icon):
        self.description=description
        self.url=url
        self.icon=icon

    def getDescription(self):
        return self.description

    def getUrl(self):
        return self.url

    def getIcon(self):
        return self.icon
    
    def toString(self):
        return(self.description+"|"+self.url+"|"+self.icon)

    @staticmethod
    def fromString(line):
        splits=line.split("|")
        description=splits[0].strip()
        url=splits[1].strip()
        icon=splits[2].strip()
        return(Video(description,url,icon))

class NewsFeed:
    def __init__(self, pathDb, logger=None):
        self.pathDb=pathDb
        self.logger=logger

    def getItemsInFeed(self,url):
      cachePathFileName=self.pathDb+'videodb.txt'
      if self.isFeedCacheAvailable(cachePathFileName,10):
        videos=self.readFeedCache(cachePathFileName)
        if videos is not None:
            return(videos)
      sections=Sections()
      videos = {}
      httpNetRequest=HttpNetRequest()
      response=httpNetRequest=httpNetRequest.getHttpNetRequest(url)
      status=response.status_code
      searchIndex=0
      response.close()
      if status!=200:
          return None
      while -1!= searchIndex:
        video, searchIndex = sections.getItemsInSection(response.text,"article",searchIndex)
        if video is not None and not (video.description in videos):
            videos[video.description]=video
      videoList=list(videos.values())
      self.writeFeedCache(cachePathFileName,videoList)
      return (videoList)

    def readFeedCache(self,pathFileName):
        try:
          videos=[]  
          with open(pathFileName,"r",encoding='utf-8') as inputStream:
            for line in inputStream:
                video=Video.fromString(line)
                # splits=line.split("|")
                # description=splits[0].strip()
                # url=splits[1].strip()
                # video=Video(description,url)
                videos.append(video)
          inputStream.close()
          return(videos)
        except:
          self.WriteLog(traceback.format_exc())
          return(None)

    def writeFeedCache(self,pathFileName,videos):
        try:
          with open(pathFileName,"w",encoding='utf-8') as outputStream:
            for video in videos:
                outputStream.write(video.toString()+"\n")
          outputStream.close()
          return(videos)
        except:
          self.WriteLog(traceback.format_exc())
          return(videos)

    def isFeedCacheAvailable(self,pathFileName,expireMinutes):
        try:
          self.WriteLog('Inspecting cache file {pathFileName}'.format(pathFileName=pathFileName))
          if not os.path.isfile(pathFileName):
            return(False)
          modifiedTime=os.path.getmtime(pathFileName)
          convertTime=time.localtime(modifiedTime)
          formatTime=time.strftime('%d%m%Y %H:%M:%S',convertTime)
          fileDateTime=datetime.datetime.strptime(formatTime,'%d%m%Y %H:%M:%S')
          currentTime=datetime.datetime.now()
          timedelta=currentTime-fileDateTime
          hours, hremainder = divmod(timedelta.seconds,3600)
          minutes, mremainder = divmod(timedelta.seconds,60)
          self.WriteLog('file is  = "{age}" hours old'.format(age=hours))
          self.WriteLog('file is  = "{age}" minutes old'.format(age=minutes))
          if hours > 1 or minutes > expireMinutes:
            return(False)
          return (True)
        except:
          self.WriteLog(traceback.format_exc());
          return(False)

    def WriteLog(self,message):
        if self.logger is not None:
            self.logger.write(message)
        else:
            print(message)

class Sections:
    def __init__(self):
      self.dummy=None

    def getItemsInSection(self, strInput, sectionName, searchIndex):
        video=None
        startSection='<'+sectionName
        endSection='</'+sectionName

        startIndex=strInput.find(startSection,searchIndex)
        if -1 == startIndex:
            searchIndex=-1
            return video, searchIndex

        endIndex=strInput.find(endSection,startIndex)
        if -1 == endIndex:
            searchIndex=-1
            return video, searchIndex

        searchIndex=endIndex+len(endSection)
        strContainingString=strInput[startIndex:endIndex+1+len(endSection)]

        if not strContainingString or strContainingString=="":
            return video, searchIndex

        indexPreview=strContainingString.find("preview=\"")
        if -1 == indexPreview:
            return video, searchIndex
        previewUrl=strContainingString[indexPreview:]
        previewUrl=self.betweenString(previewUrl,'"','"')
        if "tokenvod" in previewUrl:
            return video, searchIndex

        indexDescription=strContainingString.index("alt=\"")
        description=strContainingString[indexDescription:]
        description=self.betweenString(description,'"','"')
        description=self.removeHtml(description)
        description=description.replace("- Fox News","")
        if "vod.foxbusiness" in description:
            return video, searchIndex
        indexDuration=strContainingString.index("<div class=\"duration\">")
        if -1 != indexDuration:
            strDuration=strContainingString[indexDuration:]
            strDuration=self.betweenString(strDuration,">","<")
            description=description+" - "+strDuration
        indexPublication=strContainingString.index("<div class=\"pub-date\">")
        if -1 != indexPublication:
            strPublication=strContainingString[indexPublication:]
            strPublication=self.betweenString(strPublication,"<time>","</time>")
            description=description+" ("+strPublication+")"
        icon=None
        indexIcon=strContainingString.index("srcset=")
        if -1 != indexIcon:
            icon=strContainingString[indexIcon:]
            icon=self.betweenString(icon,"\"","\"")
            splits=icon.split(',')
            icon=self.betweenString(splits[len(splits)-1],None,'?')
            icon=icon.strip()
#            icon=self.betweenString(icon,"\"","?")
        video=Video(description,previewUrl,icon)
        return video, searchIndex

    def betweenString(self, strItem, strBegin, strEnd ):
        if strItem is None:
            return None
        index=-1
        if strBegin is None:
            index=0
        else:
            index = strItem.index(strBegin)
        if -1==index:
            return None
        str=None
        if strBegin is not None:
            str=strItem[index+len(strBegin):]
        else:
            str=strItem
        if strEnd is None:
            return str
        index=str.index(strEnd)
        if -1==index :
            return None
        sb=""
        for strIndex in range(0, len(str)-1):
            if index==strIndex:
                break
            sb=sb+str[strIndex]
        return (sb)

    def removeHtml(self,strItem):
        if strItem is None:
            return None
        codes={"&#x27;","&#187;"}
        for code in codes:
            strItem=strItem.replace(code,"'")
        strItem=strItem.replace("&amp;","&")
        strItem=strItem.replace("&#x2018;","'")
        strItem=strItem.replace("&#x2019;","'")
        strItem=strItem.replace("&#x2014;","-")
        strItem=strItem.replace("???","'")
        return strItem

class HttpNetRequest:
    def __init__(self):
        self.Message=""

    def getHttpNetRequest(self,url):
        response=requests.get(url)
        return response


newsFeed=NewsFeed('/home/pi/.kodi/addons/plugin.video.fox.news/resources/lib/')
#newsFeed.isFeedCacheAvailable()
videos=newsFeed.getItemsInFeed("https://www.foxnews.com/video")
for video in videos:
    print(video.description)
  


