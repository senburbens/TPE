Mark Needham
Thoughts on Software Development
Neo4j: Building a topic graph with Prismatic Interest Graph API
2 Comments

Over the last few weeks I’ve been using various NLP libraries to derive topics for my corpus of How I met your mother episodes without success and was therefore enthused to see the release of Prismatic’s Interest Graph API

The Interest Graph API exposes a web service to which you feed a block of text and get back a set of topics and associated score.

It has been trained over the last few years with millions of articles that people share on their social media accounts and in my experience using Prismatic the topics have been very useful for finding new material to read.

The first step is to head to interest-graph.getprismatic.com and get an API key which will be emailed to you.

Having done that we’re ready to make some calls to the API and get back some topics.

I’m going to use Python to call the API and I’ve found the requests library the easiest library to use for this type of work. Our call to the API looks like this:

import requests
payload = { 'title': "insert title of article here",
            'body': "insert body of text here"),
            'api-token': "insert token sent by email here"}
r = requests.post("http://interest-graph.getprismatic.com/text/topic", data=payload)
One thing to keep in mind is that the API is rate limited to 20 requests a second so we need to restrict our requests or we’re going to receive error response codes. Luckily I came across an excellent blog post showing how to write a decorator around a function and only allow it to execute at a certain frequency.

To rate limit our calls to the Interest Graph we need to pull the above code into a function and annotate it appropriately:

import time
 
def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate
 
@RateLimited(0.3)
def topics(title, body):
    payload = { 'title': title,
                'body': body,
                'api-token': "insert token sent by email here"}
    r = requests.post("http://interest-graph.getprismatic.com/text/topic", data=payload)
    return r
The text I want to classify is stored in a CSV file – one sentence per line. Here’s a sample:

$ head -n 10 data/import/sentences.csv
SentenceId,EpisodeId,Season,Episode,Sentence
1,1,1,1,Pilot
2,1,1,1,Scene One
3,1,1,1,[Title: The Year 2030]
4,1,1,1,"Narrator: Kids, I'm going to tell you an incredible story. The story of how I met your mother"
5,1,1,1,Son: Are we being punished for something?
6,1,1,1,Narrator: No
7,1,1,1,"Daughter: Yeah, is this going to take a while?"
8,1,1,1,"Narrator: Yes. (Kids are annoyed) Twenty-five years ago, before I was dad, I had this whole other life."
9,1,1,1,"(Music Plays, Title ""How I Met Your Mother"" appears)"
We’ll also need to refer to another CSV file to get the title of each episode since it isn’t being stored with the sentence:

$ head -n 10 data/import/episodes_full.csv
NumberOverall,NumberInSeason,Episode,Season,DateAired,Timestamp,Title,Director,Viewers,Writers,Rating
1,1,/wiki/Pilot,1,"September 19, 2005",1127084400,Pilot,Pamela Fryman,10.94,"Carter Bays,Craig Thomas",68
2,2,/wiki/Purple_Giraffe,1,"September 26, 2005",1127689200,Purple Giraffe,Pamela Fryman,10.40,"Carter Bays,Craig Thomas",63
3,3,/wiki/Sweet_Taste_of_Liberty,1,"October 3, 2005",1128294000,Sweet Taste of Liberty,Pamela Fryman,10.44,"Phil Lord,Chris Miller",67
4,4,/wiki/Return_of_the_Shirt,1,"October 10, 2005",1128898800,Return of the Shirt,Pamela Fryman,9.84,Kourtney Kang,59
5,5,/wiki/Okay_Awesome,1,"October 17, 2005",1129503600,Okay Awesome,Pamela Fryman,10.14,Chris Harris,53
6,6,/wiki/Slutty_Pumpkin,1,"October 24, 2005",1130108400,Slutty Pumpkin,Pamela Fryman,10.89,Brenda Hsueh,62
7,7,/wiki/Matchmaker,1,"November 7, 2005",1131321600,Matchmaker,Pamela Fryman,10.55,"Sam Johnson,Chris Marcil",57
8,8,/wiki/The_Duel,1,"November 14, 2005",1131926400,The Duel,Pamela Fryman,10.35,Gloria Calderon Kellett,46
9,9,/wiki/Belly_Full_of_Turkey,1,"November 21, 2005",1132531200,Belly Full of Turkey,Pamela Fryman,10.29,"Phil Lord,Chris Miller",60
Now we need to get our episode titles and transcripts ready to pass to the topics function. Since we’ve only got ~ 200 episodes we can create a dictionary to store that data:

episodes = {}
with open("data/import/episodes_full.csv", "r") as episodesfile:
    episodes_reader = csv.reader(episodesfile, delimiter=",")
    episodes_reader.next()
    for episode in episodes_reader:
        episodes[int(episode[0])] = {"title": episode[6], "sentences" : [] }
 
with open("data/import/sentences.csv", "r") as sentencesfile:
     sentences_reader = csv.reader(sentencesfile, delimiter=",")
     sentences_reader.next()
     for sentence in sentences_reader:
         episodes[int(sentence[1])]["sentences"].append(sentence[4])
 
>>> episodes[1]["title"]
'Pilot'
>>> episodes[1]["sentences"][:5]
['Pilot', 'Scene One', '[Title: The Year 2030]', "Narrator: Kids, I'm going to tell you an incredible story. The story of how I met your mother", 'Son: Are we being punished for something?']
Now we’re going to loop through each of the episodes, call topics and write the result into a CSV file so we can load it into Neo4j afterwards to explore the data:

import json
 
with open("data/import/topics.csv", "w") as topicsfile:
    topics_writer = csv.writer(topicsfile, delimiter=",")
    topics_writer.writerow(["EpisodeId", "TopicId", "Topic", "Score"])
 
    for episode_id, episode in episodes.iteritems():
        tmp = topics(episode["title"], "".join(episode["sentences"]).json()
        print episode_id, tmp
        for topic in tmp['topics']:
            topics_writer.writerow([episode_id, topic["id"], topic["topic"], topic["score"]])
It takes about 10 minutes to run and this is a sample of the output:

$ head -n 10 data/import/topics.csv
EpisodeId,TopicId,Topic,Score
1,1519,Fiction,0.5798245566455255
1,2015,Humour,0.565154963605359
1,24031,Laughing,0.5587120401021765
1,16693,Flirting,0.5514098189505282
1,1163,Dating and Courtship,0.5487490108554022
1,2386,Kissing,0.5476185929151934
1,31929,Puns,0.5375100569837977
2,24031,Laughing,0.5670926949850333
2,1519,Fiction,0.5396488295397263
We’ll use Neo4j’s LOAD CSV command to load the data in:

// make sure the topics exist
LOAD CSV WITH HEADERS FROM "file:///Users/markneedham/projects/neo4j-himym/data/import/topics.csv" AS row
MERGE (topic:Topic {id: TOINT(row.TopicId)})
ON CREATE SET topic.value = row.Topic
// make sure the topics exist
LOAD CSV WITH HEADERS FROM "file:///Users/markneedham/projects/neo4j-himym/data/import/topics.csv" AS row
MERGE (topic:Topic {id: TOINT(row.TopicId)})
ON CREATE SET topic.value = row.Topic
// now link the episodes and topics
LOAD CSV WITH HEADERS FROM "file:///Users/markneedham/projects/neo4j-himym/data/import/topics.csv" AS row
MATCH (topic:Topic {id: TOINT(row.TopicId)})
MATCH (episode:Episode {id: TOINT(row.EpisodeId)})
MERGE (episode)-[:TOPIC {score: TOFLOAT(row.Score)}]->(topic)
We’ll assume that the episodes and seasons are already loaded – the commands to load those in are on github.

We can now write some queries against our topic graph. We’ll start simple – show me the topics for an episode:

MATCH (episode:Episode {id: 1})-[r:TOPIC]->(topic)
RETURN topic, r
Graph

Let’s say we liked the ‘Puns’ aspect of the Pilot episode and want to find out which other episodes had puns. The following query would let us find those:

MATCH (episode:Episode {id: 1})-[r:TOPIC]->(topic {value: "Puns"})<-[:TOPIC]-(other)
RETURN episode, topic, other
Graph  1

Or maybe we want to find the episode which has the most topics in common:

MATCH (episode:Episode {id: 1})-[:TOPIC]->(topic),
      (topic)<-[r:TOPIC]-(otherEpisode)
RETURN otherEpisode.title as episode, COUNT(r) AS topicsInCommon
ORDER BY topicsInCommon DESC
LIMIT 10
==> +------------------------------------------------+
==> | episode                       | topicsInCommon |
==> +------------------------------------------------+
==> | "Purple Giraffe"              | 6              |
==> | "Ten Sessions"                | 5              |
==> | "Farhampton"                  | 4              |
==> | "The Three Days Rule"         | 4              |
==> | "How I Met Everyone Else"     | 4              |
==> | "The Time Travelers"          | 4              |
==> | "Mary the Paralegal"          | 4              |
==> | "Lobster Crawl"               | 4              |
==> | "The Magician's Code, Part 2" | 4              |
==> | "Slutty Pumpkin"              | 4              |
==> +------------------------------------------------+
==> 10 rows
We could then tweak that query to get the names of those topics:

MATCH (episode:Episode {id: 1})-[:TOPIC]->(topic),
      (topic)<-[r:TOPIC]-(otherEpisode)-[:IN_SEASON]->(season)
RETURN otherEpisode.title as episode, season.number AS season, COUNT(r) AS topicsInCommon, COLLECT(topic.value)
ORDER BY topicsInCommon DESC
LIMIT 10
 
==> +-----------------------------------------------------------------------------------------------------------------------------------+
==> | episode                   | season | topicsInCommon | COLLECT(topic.value)                                                        |
==> +-----------------------------------------------------------------------------------------------------------------------------------+
==> | "Purple Giraffe"          | "1"    | 6              | ["Humour","Fiction","Kissing","Dating and Courtship","Flirting","Laughing"] |
==> | "Ten Sessions"            | "3"    | 5              | ["Humour","Puns","Dating and Courtship","Flirting","Laughing"]              |
==> | "How I Met Everyone Else" | "3"    | 4              | ["Humour","Fiction","Dating and Courtship","Laughing"]                      |
==> | "Farhampton"              | "8"    | 4              | ["Humour","Fiction","Kissing","Dating and Courtship"]                       |
==> | "Bedtime Stories"         | "9"    | 4              | ["Humour","Puns","Dating and Courtship","Laughing"]                         |
==> | "Definitions"             | "5"    | 4              | ["Kissing","Dating and Courtship","Flirting","Laughing"]                    |
==> | "Lobster Crawl"           | "8"    | 4              | ["Humour","Dating and Courtship","Flirting","Laughing"]                     |
==> | "Little Boys"             | "3"    | 4              | ["Humour","Puns","Dating and Courtship","Laughing"]                         |
==> | "Wait for It"             | "3"    | 4              | ["Fiction","Puns","Flirting","Laughing"]                                    |
==> | "Mary the Paralegal"      | "1"    | 4              | ["Humour","Dating and Courtship","Flirting","Laughing"]                     |
==> +-----------------------------------------------------------------------------------------------------------------------------------+
Overall 168 (out of 208) of the other episodes have a topic in common with the first episode so perhaps just having a topic in common isn’t the best indication of similarity.

An interesting next step would be to calculate cosine or jaccard similarity between the episodes and store that value in the graph for querying later on.

I’ve also calculated the most common bigrams across all the transcripts so it would be interesting to see if there are any interesting insights at the intersection of episodes, topics and phrases.

Be Sociable, Share!

inShare
 
Written by Mark Needham
February 13th, 2015 at 11:38 pm
Posted in neo4j,Python
Tagged with neo4j
« Python/gensim: Creating bigrams over How I met your mother transcriptsPython/scikit-learn: Calculating TF/IDF on How I met your mother transcripts »


Search for: 
 Search
Archives
Archives 
Categories
.NET (67)
Agile (61)
Distributed Agile (14)
Algorithms (12)
Android (11)
Book Club (24)
Books (36)
Build (25)
Coding (113)
Code Katas (2)
Incremental Refactoring (9)
Coding Dojo (23)
Communication (21)
Conferences (14)
QCon (4)
XP 2011 (5)
XP Day (4)
Data Science (14)
Databases (175)
CouchDB (4)
Mark Logic (2)
neo4j (166)
PostgreSQL (2)
Deliberate Practice (2)
DevOps (21)
Docker (1)
Domain Driven Design (12)
Feedback (9)
Graph Processing (2)
Hadoop (3)
Hibernate (7)
Hiring (3)
iPad (2)
jQuery (8)
Kubernetes (2)
Languages (478)
Clojure (45)
F# (54)
Go (4)
Haskell (46)
J (1)
Java (43)
Javascript (22)
Objective C (4)
Python (70)
R (97)
Ruby (63)
Scala (34)
Lean (3)
Learning (32)
Machine Learning (20)
Messaging (2)
Micro Services (5)
Networking (6)
OOP (7)
Organisational Patterns (1)
Pair Programming (28)
Product Development (1)
QTB (5)
Ranking Systems (4)
Reading Code (7)
Scripting (45)
Batch Scripting (4)
Shell Scripting (41)
SICP (1)
Software Development (277)
Spark (10)
Systems Thinking (7)
Testing (66)
ThoughtWorks University (21)
Version Control (17)
The Journalist template by Lucian E. Marin — Built for WordPress
