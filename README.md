# CDN

## High Level Approach
### DNS SERVER
**Implementation of a DNS server that dynamically returns IP addresses based on your mapping code:**

The DNS Server has a UDP socket to handle all the requests. The incoming queries are matched to their IP addresses. The source IP address is then sent to the CDN to choose the best Replica IP for this. After the IP has been fetched, it is sent back to the Client.

**Implementation of a system that maps IPs to nearby replica servers**

For our DNS server, we decided to use geolocation measurements to determine the mapping of given IPs. We extract the source IP address of the incoming DNS query, use an API (ipinfodb, discussed more below) to find its latitude and longitude coordinates, and then calculate its distance to all the EC2 nodes with the Haversine formula. From there, the node with the shortest distance to the IP address is selected, packaged up into a DNS response, and sent back to the client.

### HTTP SERVER

**Implementation of a HTTP server that efficiently fetches content from the origin on-demand and optimizes the cache hit ratio**
The Caching Policy in HTTPServer is loosely structured around the ‘Least Frequently Recently Used’ (LFRU) algorithm. It follows an algorithm that combines the benefits of 'Least Frequently Used' (LFU) and 'Least Recently Used' (LRU) schemes. 
- The Cache is partitioned into two components - The Primary Cache (7.8MB) and a Mini Cache (2MB). 
- The Primary Cache initially stores the most popular files. This content is based on the pagefile.csv file. Since the request frequency for each piece of content in the Origin Server follows a Zipf distribution, the popularity of the content can be estimated.
- Each time the HTTP Server receives a resource request from the Client, the CDN checks for the content in it's prepopulated Cache. If available, HTTP Server sends it to the Client.
- If the content is not available, the CDN sends a GET request to the Origin Server for the resource. If the Origin Server responds with a status code 200 along with the resource, the HTTP Server relays the content to the Client. All requests made (for the resources) are maintained in a queue called ‘queue_history’. 
- Once the content has been sent, it is added to the Mini Cache. The Mini Cache is initially empty and is populated with the most recently called files. The Hit rate and the Miss rate for each file is closely monitored simultaneously. 
- The replacement strategy within the Mini Cache is based on the LFU (Least Frequently Used) algorithm where the priority is given to the most frequently requested content. The least frequently used content (i.e with the highest miss rate) is replaced with the most recently requested file. 
- If any particular content in the Mini Cache file is highly popular, the content gets qualified to be added to the Primary Cache. This prepopulated Primary Cache first makes room by applying the LRU (Least Recently Used) Algorithm. The least recently used content (decided based on the queue_history) is removed from the Primary Cache and the highly popular content from Mini Cache is added.

### Performance Enhancing Techniques
- GZIP has been used to de/compress the data passed instead of LZMA. This assisted us in successfully decompressing the requested data sent to the Client for memory space optimization.
- Usage of a mini cache to keep track of recent requests along with a larger cache of the most popular requests, in addition to utilizing a hit-miss dictionary for our mini cache that we use to determine which file to remove from the mini cache by keeping track of how often pages are called (hit count) and how many times they haven’t been called (miss count). 
### Challenges
- We had a difficult time integrating Scamper with our scripts.  We did not use GeoIP Block Location approach since the chances of a request hitting within the same IP Block seems low. We spent a huge amount of time trying to debug and ultimately could not use this for Active Measurements.
- Choosing the most efficient Caching policy was tricky. We took various factors (popularity of file, frequency of hits and misses) and divided the Cache memory. We combined LRU and LFU techniques.
- Handling Memory Error and Disk Quota Exceeded errors for larger files received from the origin.
- Storing content (with special characters in names) as files since they do not accept special characters for the files names.We fixed this by looking for one of these special characters and then replacing it with either the ASCII conversion or if it was an * we replaced it with an underscore. This allowed us to save files with special characters. 
- Initially, file compression was challenging using LZMA. We faced several Memory Errors and returned compressed data for large files. We switched to Gzip and successfully sent the correct data for larger files.
- Implementation of IP Geolocation took time as we had to decide how to fetch the location of the IP Address along with passing credentials. We registered to https://ipinfodb.com/ for an API key. This is an online IP Geolocation information service. We handled the rate limit drawback (2 queries per second) using sleep().
### Future Work
If we had more time on our hands, we would have worked on:
- Multithreading: Add it into our HTTPServer to grab requests from the client and relay them back from the Origin Server/Cache. It has been difficult at the moment with the limited memory space.
- Memory Space Utilization: Optimizing the memory space for our Primary Cache and Mini Cache. 
- Mapping to Replica Server: Successfully be able to use Scamper and  factors for Active Measurements and hence enhance the Mapping efficiency.
- Scalability: We would aim to handle more requests sent out from the client and make our Server robust.
- IP Geolocation: Find an approach that would eliminate the current rate limit of 2 queries per second due to the API Server.

