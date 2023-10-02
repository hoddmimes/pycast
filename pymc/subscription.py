'''
Copyright 2023 Hoddmimes Solutions AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from __future__ import annotations
from typing import Callable
import io

class SubjectTokenParser:
    TOKEN_DELIMITER = '/'

    def __init__(self, subject: str):
        self.position: int = 0
        self.strarr = self._useIndexOf(subject, 0, 0)


    def size(self) -> int:
       return len(self.strarr)



    def getNextElement(self) -> str:
        if self.position >= len(self.strarr):
            return None
        _str = self.strarr[ self.position]
        self.position += 1
        return _str

    def hasMore(self) ->bool:
        if self.position < len(self.strarr):
            return True
        self.position = 0
        return False

    def setNewToken(self, subject: str ):
        self.position = 0
        self.strarr = self._useIndexOf(subject, 0, 0)

    def _useIndexOf(self, inStr:str, cnt:int , pos:int )-> []:
        # Recursive version...

        _nextpos:int = inStr.find(self.TOKEN_DELIMITER, pos)
        if _nextpos != -1:
            _arr:[] = self._useIndexOf(inStr, cnt + 1, _nextpos + 1)
            if (_nextpos - pos) > 0:
                _arr.insert( 0, inStr[ pos: _nextpos])
            return _arr
        else:
            _arr = []
            _arr.insert(0, inStr[pos:len(inStr)])
            return _arr


class Subscription:
    def __init__(self, subject:str, callback: Callable[ [object], None], callbackParameter: object ):
        self.subject = subject
        self.callback: Callable[ [object], None] = callback
        self.callback_parameter : object = callbackParameter


class KeyNode:
    TYPE_NORMAL: int = 0
    TYPE_WILDCARD:int = 1
    TYPE_WILDREST: int = 2


    DELIMITER = '/'
    WILDCARD = "*"
    WILDREST = "..."

    def __init__(self, key:str ):
        self.key = key
        self.children : dict[str, KeyNode] = None
        self.wildcard_child : KeyNode = None
        self.wildcard_rest_child: KeyNode = None
        self.subscriptions:list[Subscription] = None

        if key == self.WILDCARD:
            self.type = self.TYPE_WILDCARD
        elif key == self.WILDREST:
            self.type = self.TYPE_WILDREST
        else:
            self.type = self.TYPE_NORMAL

    def toString(self) -> str:

        _outbuf = io.StringIO()
        _outbuf.write("KEY: " + self.key)

        if self.subscriptions:
            _outbuf.write(" subscriptions: " + str(len(self.subscriptions)))
        else:
            _outbuf.write(" subscriptions: 0")


        if self.wildcard_rest_child:
            _outbuf.write(" wldcrd-rest: True")


        childKeys = io.StringIO()
        if self.children:
            for kn in self.children.values():
                childKeys.write(str(kn.key) + " ")

        if self.wildcard_child:
            childKeys.write("*")

        if len(childKeys.getvalue()) > 0:
            _outbuf.write( childKeys.getvalue())

        return _outbuf.getvalue()



    def addChild(self, childKey: str) -> KeyNode:
        if self.type == self.WILDREST:
            raise Exception( "Can not not add child to a \"WildcardRest\" node")

        tKeyNode = None

        if childKey == self.WILDCARD:
            if not self.wildcard_child:
               self.wildcard_child = KeyNode(childKey)
               return self.wildcard_child
        elif childKey == self.WILDREST:
            if not self.wildcard_rest_child:
                self.wildcard_rest_child = KeyNode(childKey)
            return self.wildcard_rest_child
        else:
            if not self.children:
                self.children = {}  #<String, KeyNode>()
            tKeyNode = self.children.get(childKey)
            if not tKeyNode:
                tKeyNode = KeyNode(childKey)
                self.children[childKey] = tKeyNode
            return tKeyNode


    def addSubscription(self, subjectName:str, callback: Callable[ [str, bytes, object, int,  int], None], callbackParameter: object) -> Subscription:
        tSubscription:Subscription = Subscription(subjectName, callback, callbackParameter )
        if not self.subscriptions:
            self.subscriptions = []
        self.subscriptions.append(tSubscription)
        return tSubscription

    def subscriptionsToString(self, outbuf:io.StringIO, prefix:str ):
        if self.subscriptions:
            for s in self.subscriptions:
                outbuf.write("References: {} Topic: {}/{}\n".format(len(self.subscriptions), prefix, self.key))

        if self.key == 'ROOT':
            if self.children:
                for kn in self.children.values():
                    kn.subscriptionsToString( outbuf, "")

            if self.wildcard_child:
                self.wildcard_child.subscriptionsToString(outbuf, "")

            if self.wildcard_rest_child:
                self.wildcard_rest_child.subscriptionsToString(outbuf, "")
        else:
            if self.children:
                for kn in self.children.values():
                    kn.subscriptionsToString(outbuf, prefix + "/" + self.key)

            if self.wildcard_child:
                self.wildcard_child.subscriptionsToString(outbuf, prefix + "/" + self.key)

            if self.wildcard_rest_child:
                self.wildcard_rest_child.subscriptionsToString(outbuf, prefix + "/" + self.key)


    def getActiveSubscriptionsStrings(self, vector: list[str], prefix:str ):
        if self.subscriptions:
            for s in self.subscriptions:
                vector.append("References: {} Topic: {}/{}".format(len(self.subscriptions), prefix, self.key))

        if self.key == 'ROOT':
            if self.children:
                for kn in self.children.values():
                    kn.getActiveSubscriptionsStrings( vector, "")

            if self.wildcard_child:
                self.wildcard_child.getActiveSubscriptionsStrings(vector, "")

            if self.wildcard_rest_child:
                self.wildcard_rest_child.getActiveSubscriptionsStrings(vector, "")
        else:
            if self.children:
                for kn in self.children.values():
                    kn.getActiveSubscriptionsStrings(vector, prefix + "/" + self.key)


            if self.wildcard_child:
                self.wildcard_child.getActiveSubscriptionsStrings(vector, prefix + "/" + self.key)

            if self.wildcard_rest_child:
                self.wildcard_rest_child.getActiveSubscriptionsStrings(vector, prefix + "/" + self.key)

    def removeAll(self):

        if self.wildcard_child:
            self.wildcard_child.removeAll()

        if self.wildcard_rest_child:
            self.wildcard_rest_child.removeAll()

        self.wildcard_child = None
        self.wildcard_rest_child = None

        if self.children:
            for kn in self.children.values():
                kn.removeAll()
            self.children = None

    def countActiveSubscriptions(self) ->int:
        tCount:int  = 0

        if self.children:
            for kn in self.children.values():
                tCount += kn.countActiveSubscriptions()

        if  self.subscriptions:
            tCount += len(self.subscriptions)

        if self.wildcard_child:
            tCount += self.wildcard_child.countActiveSubscriptions()

        if self.wildcard_rest_child:
            tCount += self.wildcard_rest_child.countActiveSubscriptions()

        return tCount


    def matchAny(self, keys: SubjectTokenParser ) -> bool:
        # Traversed the whole key look if there are any subscriber at this level if so return true
        if not keys.hasMore():
            if self.subscriptions and len(self.subscriptions) > 0:
                return True
            else:
                return False

        # Examine if there are any wildcard subscribers at this level if so return true
        if self.wildcard_rest_child and len(self.wildcard_rest_child.subscriptions) > 0:
            return True

        if self.wildcard_child:
            keys.getNextElement()
            for kn in self.wildcard_child:
                if self.wildcard_child.matchAny(keys):
                    return True

        if self.children:
            kn = self.children.get( keys.getNextElement())
            if kn:
                return kn.matchAny( keys )

        return False


    def traverse(self, level:int):

        tOutbuf = io.StringIO()
        for i in range( 2 * level ):
            tOutbuf.write(' ')

        tOutbuf.write("key: " + self.key)

        if self.subscriptions:
            tOutbuf.write(" subscriptions: " + str(len(self.subscriptions)))
        else:
            tOutbuf.write(" subscriptions: 0")

        if self.wildcard_child:
            tOutbuf.write(" wldcrd: True")

        if self.wildcard_rest_child:
            tOutbuf.write(" wldcrd-rest: True")

        print( tOutbuf.getvalue())

        if self.children:
            for kn in self.children.values():
                kn.traverse(level+1)

        if self.wildcard_child:
            self.wildcard_child.traverse(level + 1)




    def matchRecursive(self, subjectName:str,  keys: SubjectTokenParser, data: bytes, appId:int, queueLength:int):
        if not keys.hasMore():
            if self.subscriptions:
                for sub in self.subscriptions:
                    sub.callback(subjectName, data, sub.callback_parameter, appId, queueLength)

        else:
            if self.children:
                kn = self.children.get(keys.getNextElement())
                if kn:
                    kn.matchRecursive( subjectName, keys, data, appId, queueLength)


            if self.wildcard_child:
                keys.getNextElement()
                self.wildcard_child.matchRecursive(subjectName, keys, data, appId, queueLength)

            if self.wildcard_rest_child:
                if self.wildcard_rest_child.subscriptions:
                    for sub in self.wildcard_rest_child.subscriptions:
                        sub.callback(subjectName, data, sub.callback_parameter, appId, queueLength)


class SubscriptionFilter:

    def __init__(self):
        self.mRoot = KeyNode("ROOT")
        self.mSubscriptionMap: dict[object, KeyNode] = dict()

    def getActiveSubscriptionsCount(self) -> int:
        return self.mRoot.countActiveSubscriptions()


    def add(self, subjectName: str,  callback: Callable[[str, bytes, object, int, int], None],  callbackParameter: object) -> object:
        tKeys: SubjectTokenParser =  SubjectTokenParser(subjectName)
        if not tKeys.hasMore():
            raise Exception("Invalid pSubjectName: {} ".format(subjectName))

        tKeyNode: KeyNode = self.mRoot
        while tKeys.hasMore():
            tKey = tKeys.getNextElement()
            tKeyNode = tKeyNode.addChild(tKey)
        return tKeyNode.addSubscription( subjectName, callback, callbackParameter)

    def match( self, subjectName:str , data:bytes, appId:int, queueLength:int ):
        tKeys:SubjectTokenParser = SubjectTokenParser(subjectName)
        self.mRoot.matchRecursive(subjectName, tKeys, data, appId, queueLength)

    def matchAny( self, subjectName:str ):
        tKeys:SubjectTokenParser = SubjectTokenParser(subjectName)
        return self.mRoot.matchAny(tKeys)

    def getActiveSubscriptionsStrings(self) ->list[str]:
        _list: list[str] = []
        self.mRoot.getActiveSubscriptionsStrings(_list, "")
        return _list

    def toString(self) -> str:
        tOutbuf = io.StringIO()
        self.mRoot.subscriptionsToString(tOutbuf, "")
        return tOutbuf.getvalue()



def main_token():
    stp = SubjectTokenParser("/foo/bar/frotz")
    while stp.hasMore():
        print( stp.getNextElement())

    stp.setNewToken("/abc/123423/k/end")
    while stp.hasMore():
        print( stp.getNextElement())

def subscriptionCallback( subjectName:str, data:bytes, callbackParameter:object, appId:int, queueLength: int):
    print(" callback subject: {} data: {} param: {}    app-id: {} quelen: {} ".format( subjectName, data.decode('utf-8'), str( callbackParameter), str(appId), str( queueLength)))


def main_filter():
    filter:SubscriptionFilter = SubscriptionFilter()
    # filter.add("/foo/bar/fie",subscriptionCallback, "/foo/bar/fie" )
    # filter.add("/foo/*/zzz",subscriptionCallback, "/foo/*/zzz" )
    # filter.add("/foo/...",subscriptionCallback, "/foo/..." )
    #filter.add("/frotz/a/b/c",subscriptionCallback, "/frotz/a/b/c" )
    filter.add("/...", subscriptionCallback, "/..." )

    filter.match("/foo/bar/fie", bytes("test1".encode()), 4711,1)
    print( filter.toString())

if __name__ == '__main__':
    main_filter()