# pycast
Python pub/sub utility for true one-to-many real time reliable distribution.

**pycast** is using  IP [multicast](http://en.wikipedia.org/wiki/Multicast) ([RFC 1112](http://www.ietf.org/rfc/rfc1112.txt)) when communicating. IP mulicasting is _not a reliable_ transport,
messages may get lost or delivered out of order. Pycast has mechanisms for detecting out of order and lost messages and will
recover messages transperently to the application. In the odd event of an irrecoverable message the application is notified.

## Overall Structure (objects)

- **Distributor** the main class being the handle to the pub/sub mechanism is the *Distributor* class. It is also the first instance created in a application using *pycast*.
- **DistrubtorConfiguration** holds the configuration for _pycast_ and is being passed as an in parameter when creating a _Distributor_
- **Connection** is the class encuosulate the actual communitation stream. Multiple instances  can be created, each with a unique class D multicast group and UDP port.
- **ConnectionConfiguration** holds the configuration for a _Connection_ and is the input parametter when creating a _Connection_ instance.
- **Publisher**, a publisher instance holds the interface through which the application can publish updates. When creating a publisher a _Connection_ must be specified which the updates will be sent.
- **Subscriber** a subscriber instance provides the inferace on which the application can subscribe for updates. When creating a subscriber a _Connection_ must be specified. The subscription will only match the updates sent out on the connection specified.



## Features

The main characteristics of the **_pycast_** are;

- **Error detection** and correction. _pycast_ using _Negative Acknologements_. This immplies that subscriber instances does not acknowledge each message. _Subscribers_ just acknowledge missed  when detecting missed messages or messages out of order.
- **Segmenting**, large updates may be broken up and sent in multiple packages, so there is virtually no update message size limitation.
- **Adaptive transmission holdback** When the publishing frequency of updates are low and moderate updates are published directly without any delay. When publing at a high frequency a small holdback timer may be applied to fit multiple updates into a single network package. This will in many cases increase the overall throughput and latency.
- **Topic filtering** (see below), all updates being published will be associated with a _topic_ (eg. "/foo/bar/*"). A subscriber is not receiving anything unless is setup subscriptionbs for the topics it has an interest in.
- **Performance and low latency**, _pycast_ is a _real time_ transport mechanism. No data is persisted or could be stored-and-forward. Thousends of message can be published with instant delivery (even is Python is not the ideal implementation language for this type of utility) 
- **Web Interface**, the _pycast_ utility is when starting also declaring a web interface allowing a browser to browse, various statistics for the _pycast_objects / traffic. The enabling and http port can be configured in the _DistributorConfiguration_ class.
## Topics

All information published by publisher application have an associated subject name. 
And in order for subscriber application to receive data they must setup subscriptions on subjects that they have and interest in.

Subject names are hieratical string like _“/foo/bar/fie”_. The “/” characters is used to separate levels. 
A subject name could have an arbitrary number of levels. 

The strings “*” and “…” are used to express wildcard matching 

Publisher must publish data with absolute subject names i.e. must not contain the strings “*” or “…”. 
Subscribers may use absolute subject or wildcard subject when setting up subscriptions.

Subject names are case sensitive.
Some typical matching rules.
- “/foo/bar” will not match “/foo/bar/fie”

- “/foo/\*” will  match all subjects with two levels and starting with “/foo”

- “/foo/\*/bar/\*” will match all subjects with four levels, where level one is equal with “/foo” level three
       with “/bar” and level two and four being whatever.
“/foo/bar/…” with match anything with three or more levels, starting with “/foo” and “/bar” at level one and two. 

## Exampel / Test Programs

[pycast.py](https://github.com/hoddmimes/pycast/blob/main/pycast.py) a simple combined publisher / subscriber application. Both sending and receivin updates. Probebly a good starting point to understand how things are done.

[tstpub.py](https://github.com/hoddmimes/pycast/blob/main/tstpub.py) a fairly simple configurable _publisher_ application publishing data. Probebly a good application if you would like to play around with the _pycast_ utlity. You can configure update rates, simulation of errors, logging etc.

[tstpub.py](https://github.com/hoddmimes/pycast/blob/main/tstpub.py) is a configurable _subscriber_ application that works working together with the _tstpub_ application. It will subscribe to data published by the _tstpub_ application. You can configure logging and topics to subscribe for.


## Why?

The reason for doing this was actually to grasping what Python is about. I'm not a python programmer but there has been som much fuzz about the language so
I had to try Python out. I took and one of my old java projects and decided to convert it to Python (you will probebly notice).You can get a better understanding of _pycast_
by reading about the orginal project;  [**_Distributor_** here](https://github.com/hoddmimes/Distributor)


**_The rest is as usual, in the source_**