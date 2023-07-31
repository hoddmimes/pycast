from __future__ import annotations
from typing import Callable
import io

class SubjectTokenParser:
    TOKEN_DELIMITER = '/'

    def __init__(self, subject: str):
        self.mPosition: int = 0
        self.mStrarr = self._useIndexOf(subject, 0, 0)


    def size(self) -> int:
       return len(self.mStrarr)



    def getNextElement(self) -> str:
        if self.mPosition >= len(self.mStrarr):
            return None
        tStr = self.mStrarr[ self.mPosition]
        self.mPosition += 1
        return tStr

    def hasMore(self) ->bool:
        if self.mPosition < len(self.mStrarr):
            return True
        self.mPosition = 0
        return False

    def setNewToken(self, subject: str ):
        self.mPosition = 0
        self.mStrarr = self._useIndexOf(subject, 0, 0)

    def _useIndexOf(self, inStr:str, cnt:int , pos:int )-> []:
        # Recursive version...

        tNextpos:int = inStr.find(self.TOKEN_DELIMITER, pos)
        if tNextpos != -1:
            tArr:[] = self._useIndexOf(inStr, cnt + 1, tNextpos + 1)
            if (tNextpos - pos) > 0:
                tArr.insert( 0, inStr[ pos: tNextpos])
            return tArr
        else:
            tArr = []
            tArr.insert(0, inStr[pos:len(inStr)])
            return tArr


class Subscription:
    def __init__(self, subject:str, callback: Callable[ [object], None], callbackParameter: object ):
        self.mSubject = subject
        self.mCallback: Callable[ [object], None] = callback
        self.mCallbackParameter : object = callbackParameter


class KeyNode:
    TYPE_NORMAL: int = 0
    TYPE_WILDCARD:int = 1
    TYPE_WILDREST: int = 2


    DELIMITER = '/'
    WILDCARD = "*"
    WILDREST = "..."

    def __init__(self, key:str ):
        self.mKey = key
        self.mChildren : dict[str, KeyNode] = None
        self.mWildcardChild : KeyNode = None
        self.mWildcardRestChild: KeyNode = None
        self.mSubscriptions:list[Subscription] = None

        if key == self.WILDCARD:
            self.type = self.TYPE_WILDCARD
        elif key == self.WILDREST:
            self.type = self.TYPE_WILDREST
        else:
            self.type = self.TYPE_NORMAL

    def toString(self) -> str:

        tOutbuf = io.StringIO()
        tOutbuf.write("KEY: " + self.mKey)

        if self.mSubscriptions:
            tOutbuf.write(" subscriptions: " + str(len(self.mSubscriptions)))
        else:
            tOutbuf.write(" subscriptions: 0")


        if self.mWildcardRestChild:
            tOutbuf.write(" wldcrd-rest: True")


        childKeys = io.StringIO()
        if self.children:
            for kn in self.children.values():
                childKeys.write(str(kn.mKey) + " ")

        if self.mWildcardChild:
            childKeys.write("*")

        if len(childKeys.getvalue()) > 0:
            tOutbuf.write( childKeys.getvalue())

        return tOutbuf.getvalue()





    def addChild(self, childKey: str) -> KeyNode:
        if self.type == self.WILDREST:
            raise Exception( "Can not not add child to a \"WildcardRest\" node")

        tKeyNode = None

        if childKey == self.WILDCARD:
            if not self.mWildcardChild:
               self.mWildcardChild = KeyNode(childKey)
               return self.mWildcardChild
        elif childKey == self.WILDREST:
            if not self.mWildcardRestChild:
                self.mWildcardRestChild = KeyNode(childKey)
            return self.mWildcardRestChild
        else:
            if not self.children:
                self.children = {}  #<String, KeyNode>()
            tKeyNode = self.children.get(childKey)
            if not tKeyNode:
                tKeyNode = KeyNode(childKey)
                self.children[childKey] = tKeyNode
            return tKeyNode


    def addSubscription(self, subjectName:str, callback: Callable[ [str, bytearray, object, int,  int], None], callbackParameter: object) -> Subscription:
        tSubscription:Subscription = Subscription(subjectName, callback, callbackParameter )
        if not self.mSubscriptions:
            self.mSubscriptions = []
        self.mSubscriptions.append(tSubscription)
        return tSubscription

    def subscriptionsToString(self, outbuf:io.StringIO, prefix:str ):
        if self.mSubscriptions:
            for s in self.mSubscriptions:
                outbuf.write("References: {} Topic: {}/{}\n".format(len(self.mSubscriptions), prefix, self.mKey))

        if self.mKey == 'ROOT':
            if self.children:
                for kn in self.children.values():
                    kn.subscriptionsToString( outbuf, "")

            if self.mWildcardChild:
                self.mWildcardChild.subscriptionsToString(outbuf, "")

            if self.mWildcardRestChild:
                self.mWildcardRestChild.subscriptionsToString(outbuf, "")
        else:
            if self.children:
                for kn in self.children.values():
                    kn.subscriptionsToString(outbuf, prefix + "/" + self.mKey)

            if self.mWildcardChild:
                self.mWildcardChild.subscriptionsToString(outbuf, prefix + "/" + self.mKey)

            if self.mWildcardRestChild:
                self.mWildcardRestChild.subscriptionsToString(outbuf, prefix + "/" + self.mKey)


    def getActiveSubscriptionsStrings(self, vector:[], prefix:str ):
        if self.mSubscriptions:
            for s in self.mSubscriptions:
                vector.add("References: {} Topic: {}/{}".format(len(self.mSubscriptions), prefix, self.mKey))

        if self.mKey == 'ROOT':
            if self.children:
                for kn in self.children.values():
                    kn.getActiveSubscriptionsStrings( vector, "")

            if self.mWildcardChild:
                self.mWildcardChild.getActiveSubscriptionsStrings(vector, "")

            if self.mWildcardRestChild:
                self.mWildcardRestChild.getActiveSubscriptionsStrings(vector, "")
        else:
            if self.children:
                for kn in self.children.values():
                    kn.getActiveSubscriptionsStrings(vector, prefix + "/" + self.mKey)


            if self.mWildcardChild:
                self.mWildcardChild.getActiveSubscriptionsStrings(vector, prefix + "/" + self.mKey)

            if self.mWildcardRestChild:
                self.mWildcardRestChild.getActiveSubscriptionsStrings(vector, prefix + "/" + self.mKey)

    def removeAll(self):

        if self.mWildcardChild:
            self.mWildcardChild.removeAll()

        if self.mWildcardRestChild:
            self.mWildcardRestChild.removeAll()

        self.mWildcardChild = None
        self.mWildcardRestChild = None

        if self.children:
            for kn in self.children.values():
                kn.removeAll()
            self.children = None

    def countActiveSubscriptions(self) ->int:
        tCount:int  = 0

        if self.children:
            for kn in self.children.values():
                tCount += kn.countActiveSubscriptions()

        if  self.mSubscriptions:
            tCount += len(self.mSubscriptions)

        if self.mWildcardChild:
            tCount += self.mWildcardChild.countActiveSubscriptions()

        if self.mWildcardRestChild:
            tCount += self.mWildcardRestChild.countActiveSubscriptions()

        return tCount


    def matchAny(self, keys: SubjectTokenParser ) -> bool:
        # Traversed the whole key look if there are any subscriber at this level if so return true
        if not keys.hasMore():
            if self.mSubscriptions and len(self.mSubscriptions) > 0:
                return True
            else:
                return False

        # Examine if there are any wildcard subscribers at this level if so return true
        if self.mWildcardRestChild and len(self.mWildcardRestChild.mSubscriptions) > 0:
            return True

        if self.mWildcardChild:
            keys.getNextElement()
            for kn in self.mWildcardChild:
                if self.mWildcardChild.matchAny(keys):
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

        tOutbuf.write("key: " + self.mKey)

        if self.mSubscriptions:
            tOutbuf.write(" subscriptions: " + str(len(self.mSubscriptions)))
        else:
            tOutbuf.write(" subscriptions: 0")

        if self.mWildcardChild:
            tOutbuf.write(" wldcrd: True")

        if self.mWildcardRestChild:
            tOutbuf.write(" wldcrd-rest: True")

        print( tOutbuf.getvalue())

        if self.children:
            for kn in self.children.values():
                kn.traverse(level+1)

        if self.mWildcardChild:
            self.mWildcardChild.traverse(level + 1)




    def matchRecursive(self, subjectName:str,  keys: SubjectTokenParser, data: bytearray, appId:int, queueLength:int):
        if not keys.hasMore():
            if self.mSubscriptions:
                for sub in self.mSubscriptions:
                    sub.mCallback(subjectName, data, sub.mCallbackParameter, appId, queueLength)

        else:
            if self.children:
                kn = self.mChildren.get( keys.getNextElement())
                if kn:
                    kn.matchRecursive( subjectName, keys, data, appId, queueLength)


                if self.mWildcardChild:
                    keys.getNextElement()
                    self.mWildcardChild.matchRecursive(subjectName, keys, data, appId, queueLength)

                if self.mWildcardRestChild:
                    if self.mWildcardRestChild.mSubscriptions:
                        for sub in self.mWildcardRestChild.mSubscriptions:
                            sub.mCallback(subjectName, data, sub.mCallbackParameter, appId, queueLength)


class SubscriptionFilter:

    def __init__(self):
        self.mRoot = KeyNode("ROOT")
        self.mSubscriptionMap: dict[object, KeyNode] = dict()

    def getActiveSubscriptions(self) -> int:
        return self.mRoot.countActiveSubscriptions()

    def add(self, subjectName: str,  callback: Callable[[str, bytearray, object, int, int], None],  callbackParameter: object) -> object:
        tKeys: SubjectTokenParser =  SubjectTokenParser(subjectName)
        if not tKeys.hasMore():
            raise Exception("Invalid pSubjectName: {} ".format(subjectName))

        tKeyNode: KeyNode = self.mRoot
        while tKeys.hasMore():
            tKey = tKeys.getNextElement()
            tKeyNode = tKeyNode.addChild(tKey)
        return tKeyNode.addSubscription( subjectName, callback, callbackParameter)

    def match( self, subjectName:str , data:bytearray, appId:int, queueLength:int ):
        tKeys:SubjectTokenParser = SubjectTokenParser(subjectName)
        self.mRoot.matchRecursive(subjectName, tKeys, data, appId, queueLength)

    def matchAny( self, subjectName:str ):
        tKeys:SubjectTokenParser = SubjectTokenParser(subjectName)
        return self.mRoot.matchAny(tKeys)

    def getActiveSubscriptionsStrings(self) ->[str]:
        tVector:[str] = []
        return self.mRoot.getActiveSubscriptionsStrings(tVector, "")

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

def subscriptionCallback( subjectName:str, data:bytearray, callbackParameter:object, appId:int, queueLength: int):
    print(" callback subject: {} data: {} param: {}    app-id: {} quelen: {} ".format( subjectName, data.decode('utf-8'), str( callbackParameter), str(appId), str( queueLength)))


def main_filter():
    filter:SubscriptionFilter = SubscriptionFilter()
    filter.add("/foo/bar/fie",subscriptionCallback, "/foo/bar/fie" )
    filter.add("/foo/*/zzz",subscriptionCallback, "/foo/*/zzz" )
    filter.add("/foo/...",subscriptionCallback, "/foo/..." )
    filter.add("/frotz/a/b/c",subscriptionCallback, "/frotz/a/b/c" )

    filter.match("/foo/bar/fie", bytearray("test1".encode()), 4711,1)
    print( filter.toString())

if __name__ == '__main__':
    main_filter()