from __future__ import annotations
from typing import Callable
import io

class SubjectTokenParser:
    TOKEN_DELIMITER = '/'

    def __init__(self, subject: str):
        self._position: int = 0
        self._strarr = self._useIndexOf( subject, 0, 0)


    def size(self) -> int:
       return len(self._strarr)



    def getNextElement(self) -> str:
        if self._position >= len( self._strarr):
            return None
        _str = self._strarr[ self._position]
        self._position += 1
        return _str

    def hasMore(self) ->bool:
        return self._position < len( self._strarr )

    def setNewToken(self, subject: str ):
        self._position = 0
        self._strarr = self._useIndexOf(subject, 0, 0)

    def _useIndexOf(self, inStr:str, cnt:int , pos:int )-> []:
        # Recursive version...

        _nextpos:int = inStr.find(self.TOKEN_DELIMITER, pos)
        if _nextpos != -1:
            arr:[] = self._useIndexOf(inStr, cnt + 1, _nextpos + 1)
            arr.insert( 0, inStr[ pos: _nextpos])
            return arr
        else:
            arr = []
            arr.insert(0, inStr[pos:len(inStr)])
            return arr


class Subscription:
    def __init__(self, subject:str, callback: Callable[ [object], None], callbackParameter: object ):
        self.subject = subject
        self.callback: Callable[ [object], None] = callback
        self.callbackParameter : object = callbackParameter


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
        self.wildcardChild : KeyNode = None
        self.wildcardRestChild: KeyNode = None
        self.subscriptions:list[Subscription] = None

        if key == self.WILDCARD:
            self.type = self.TYPE_WILDCARD
        elif key == self.WILDREST:
            self.type = self.TYPE_WILDREST
        else:
            self.type = self.TYPE_NORMAL



    def addChild(self, childKey: str) -> KeyNode:
        if self.type == self.WILDREST:
            raise Exception( "Can not not add child to a \"WildcardRest\" node")

        keyNode = None

        if childKey == self.WILDCARD:
            if not self.wildcardChild:
               self.wildcardChild = KeyNode(childKey)
               return self.wildcardChild
        elif childKey == self.WILDREST:
            if not self.wildcardRestChild:
                self.wildcardRestChild = KeyNode(childKey)
            return self.wildcardRestChild
        else:
            if not self.children:
                self.children = {}  #<String, KeyNode>()
            keyNode = self.children.get(childKey)
            if not keyNode:
                keyNode = KeyNode(childKey)
                self.children[childKey] = keyNode
            return keyNode


    def addSubscription(self, subjectName:str, callback: Callable[ [str, bytearray, object, int,  int], None], callbackParameter: object) -> Subscription:
        subscription:Subscription = Subscription(subjectName, callback, callbackParameter )
        if not self.subscriptions:
            self.subscriptions = []
        self.subscriptions.append( subscription )
        return subscription

    def subscriptionsToString(self, outbuf:io.StringIO, prefix:str ):
        if self.subscriptions:
            for s in self.subscriptions:
                outbuf.write("References: {} Topic: {}/{}".format( len(self.subscriptions), prefix, self.key))

        if self.key == 'ROOT':
            if self.children:
                for kn in self.children.values():
                    kn.subscriptionsToString( outbuf, "")

            if self.wildcardChild:
                self.wildcardChild.subscriptionsToString(outbuf, "")

            if self.wildcardRestChild:
                self.wildcardRestChild.subscriptionsToString(outbuf,"")
        else:
            if self.children:
                for kn in self.children.values():
                    kn.subscriptionsToString( outbuf, prefix + "/" + self.key)


            if self.wildcardChild:
                self.wildcardChild.subscriptionsToString(outbuf, prefix + "/" + self.key)

            if self.wildcardRestChild:
                self.wildcardRestChild.subscriptionsToString(outbuf, prefix + "/" + self.key)


    def getActiveSubscriptionsStrings(self, vector:[], prefix:str ):
        if self.subscriptions:
            for s in self.subscriptions:
                vector.add("References: {} Topic: {}/{}".format( len(self.subscriptions), prefix, self.key))

        if self.key == 'ROOT':
            if self.children:
                for kn in self.children.values():
                    kn.getActiveSubscriptionsStrings( vector, "")

            if self.wildcardChild:
                self.wildcardChild.getActiveSubscriptionsStrings(vector, "")

            if self.wildcardRestChild:
                self.wildcardRestChild.getActiveSubscriptionsStrings(vector,"")
        else:
            if self.children:
                for kn in self.children.values():
                    kn.getActiveSubscriptionsStrings( vector, prefix + "/" + self.key)


            if self.wildcardChild:
                self.wildcardChild.getActiveSubscriptionsStrings(vector, prefix + "/" + self.key)

            if self.wildcardRestChild:
                self.wildcardRestChild.getActiveSubscriptionsStrings(vector, prefix + "/" + self.key)

    def removeAll(self):

        if self.wildcardChild:
            self.wildcardChild.removeAll()

        if self.wildcardRestChild:
            self.wildcardRestChild.removeAll()

        self.wildcardChild = None
        self.wildcardRestChild = None

        if self.children:
            for kn in self.children.values():
                kn.removeAll()
            self.children = None

    def countActiveSubscriptions(self) ->int:
        count:int  = 0

        if self.children:
            for kn in self.children.values():
                count += kn.countActiveSubscriptions()

        if  self.subscriptions:
            count += len(self.subscriptions)

        if self.wildcardChild:
            count += self.wildcardChild.countActiveSubscriptions()

        if self.wildcardRestChild:
            count += self.wildcardRestChild.countActiveSubscriptions()

        return count


    def matchAny(self, keys: SubjectTokenParser ) -> bool:
        # Traversed the whole key look if there are any subscriber at this level if so return true
        if not keys.hasMore():
            if self.subscriptions and len(self.subscriptions) > 0:
                return True
            else:
                return False

        # Examine if there are any wildcard subscribers at this level if so return true
        if self.wildcardRestChild and len(self.wildcardRestChild.subscriptions) > 0:
            return True

        if self.wildcardChild:
            keys.getNextElement()
            for kn in self.wildcardChild:
                if self.wildcardChild.matchAny(keys):
                    return True

        if self.children:
            kn = self.children.get( keys.getNextElement())
            if kn:
                return kn.matchAny( keys )

        return False


    def matchRecursive(self, subjectName:str,  keys: SubjectTokenParser, data: bytearray, appId:int, queueLength:int):
        if not keys.hasMore():
            if self.subscriptions:
                for sub in self.subscriptions:
                    sub.callback( subjectName, data, sub.callbackParameter, appId, queueLength)

        else:
            if self.children:
                kn = self.children.get( keys.getNextElement())
                if kn:
                    kn.matchRecursive( subjectName, keys, data, appId, queueLength)


                if self.wildcardChild:
                    keys.getNextElement()
                    self.wildcardChild.matchRecursive(subjectName, keys, data, appId, queueLength)

                if self.wildcardRestChild:
                    if self.wildcardRestChild.subscriptions:
                        for sub in self.wildcardRestChild.subscriptions:
                            sub.callback( subjectName, data, sub.callbackParameter, appId, queueLength)


class SubscriptionFilter:

    def __init__(self):
        self.root = KeyNode("ROOT")
        self.subscriptionMap: dict[object, KeyNode] = dict()

    def getActiveSubscriptions(self) -> int:
        return self.root.countActiveSubscriptions()

    def add(self, subjectName: str,  callback: Callable[[str, bytearray, object, int, int], None],  callbackParameter: object) -> object:
        keys: SubjectTokenParser =  SubjectTokenParser(subjectName)
        if not keys.hasMore():
            raise Exception("Invalid pSubjectName: {} ".format(subjectName))

        keyNode: KeyNode = self.root
        while keys.hasMore():
            keyNode = keyNode.addChild(keys.getNextElement())
        print( keyNode )
        return keyNode.addSubscription( subjectName, callback, callbackParameter)

    def match( self, subjectName:str , data:bytearray, appId:int, queueLength:int ):
        keys:SubjectTokenParser = SubjectTokenParser(subjectName)
        self.root.matchRecursive(subjectName, keys, data, appId, queueLength)

    def matchAny( self, subjectName:str ):
        keys:SubjectTokenParser = SubjectTokenParser(subjectName)
        return self.root.matchAny(keys)

    def getActiveSubscriptionsStrings(self) ->[str]:
        vector:[str] = []
        return self.root.getActiveSubscriptionsStrings( vector, "")

    def toString(self) -> str:
        outbuf = io.StringIO()
        self.root.subscriptionsToString( outbuf, "" )
        return outbuf.getvalue()



def main_token():
    stp = SubjectTokenParser("/foo/bar/frotz")
    while stp.hasMore():
        print( stp.getNextElement())

    stp.setNewToken("/abc/123423/k/end")
    while stp.hasMore():
        print( stp.getNextElement())

def subscriptionCallback( subjectName:str, data:bytearray, callbackParameter:object, appId:int, queueLength: int):
    print("subject: {} data: {} param: {} app-id: {} quelen: {} ".format( subjectName), data.decode('utf-8'), str( callbackParameter), str(appId), str( queueLength))
def main_filter():
    filter:SubscriptionFilter = SubscriptionFilter()
    filter.add("/foo/bar/fie",subscriptionCallback, None )
    filter.add("/foo/*/zzz",subscriptionCallback, None )
    filter.add("/foo/...",subscriptionCallback, None )
    filter.add("/frotz/a/b/c",subscriptionCallback, None )

    print( filter.toString())

if __name__ == '__main__':
    main_filter()