import socket

class RetransmissionStatistics:
    def __init__(self):
        self.mOutStatistics = {}
        self.mInStatistics = {}
        self.mTotalIn = 0
        self.mTotalOut = 0
        self.mTotalSeen = 0

    def getRetransmissonsInfo(self):
        tRsp = DistExploreRetransmissonsRsp()
        tRsp.setTotalInRqst(self.mTotalIn)
        tRsp.setTotalOutRqst(self.mTotalOut)
        tRsp.setTotalSeenRqst(self.mTotalSeen)
        tInNodes = list(self.mInStatistics.values())
        if tInNodes:
            self.sortInNodes(tInNodes)
            tInNodeArray = []
            for node in tInNodes:
                tInNodeArray.append(node.toInString())
            tRsp.setInHosts(tInNodeArray)
        else:
            tRsp.setInHosts(None)
        tOutNodes = list(self.mOutStatistics.values())
        if tOutNodes:
            self.sortOutNodes(tOutNodes)
            tOutNodeArray = []
            for node in tOutNodes:
                tOutNodeArray.append(node.toOutString())
            tRsp.setOutHosts(tOutNodeArray)
        else:
            tRsp.setOutHosts(None)
        return tRsp

    def sortInNodes(self, pInNodes):
        if not pInNodes:
            return
        for j in range(len(pInNodes)):
            for i in range(1, len(pInNodes)):
                if pInNodes[i].mToThisNodeCount > pInNodes[i - 1].mToThisNodeCount:
                    tTmp = pInNodes[i - 1]
                    pInNodes[i - 1] = pInNodes[i]
                    pInNodes[i] = tTmp

    def sortOutNodes(self, pOutNodes):
        if not pOutNodes:
            return
        for j in range(len(pOutNodes)):
            for i in range(1, len(pOutNodes)):
                if pOutNodes[i].mOutCount > pOutNodes[i - 1].mOutCount:
                    tTmp = pOutNodes[i - 1]
                    pOutNodes[i - 1] = pOutNodes[i]
                    pOutNodes[i] = tTmp

    def getKey(self, pMcaAddress, pMcaPort, pAddress):
        tValue = ((socket.inet_aton(pMcaAddress) & 0x00ffffff) << 40) + ((socket.inet_aton(pAddress) & 0x00ffffff) << 16) + (pMcaPort & 0xffff)
        return tValue

    def updateInStatistics(self, pMcaAddress, pMcaPort, pAddress, pToThisApplication):
        tKey = self.getKey(pMcaAddress, pMcaPort, pAddress)
        tEntry = self.mInStatistics.get(tKey)
        if not tEntry:
            tEntry = NodeEntry(pMcaAddress, pMcaPort, pAddress)
            self.mInStatistics[tKey] = tEntry
        self.mTotalSeen += 1
        tEntry.mTotalInCount += 1
        if pToThisApplication:
            self.mTotalIn += 1
            tEntry.mToThisNodeCount += 1
        else:
            tEntry.mToRemoteNodeCount += 1

    def updateOutStatistics(self, pMcaAddress, pMcaPort, pAddress):
        tKey = self.getKey(pMcaAddress, pMcaPort, pAddress)
        tEntry = self.mOutStatistics.get(tKey)
        if not tEntry:
            tEntry = NodeEntry(pMcaAddress, pMcaPort, pAddress)
            self.mOutStatistics[tKey] = tEntry
        tEntry.mOutCount += 1
        self.mTotalIn += 1

    class NodeEntry:
        def __init__(self, pMcaAddress, pMcaPort, pAddress):
            self.mMcaAddress = pMcaAddress
            self.mMcaPort = pMcaPort
            self.mAddress = pAddress
            self.mToThisNodeCount = 0
            self.mToRemoteNodeCount = 0
            self.mTotalInCount = 0
            self.mOutCount = 0

        def toOutString(self):
            return "Host: " + self.mAddress + " number of outgoing retransmissions " + str(self.mOutCount)

        def toInString(self):
            return "Host: " + self.mAddress + " seen retransmissions " + str(self.mTotalInCount) + " for this hosts " + str(self.mToThisNodeCount)