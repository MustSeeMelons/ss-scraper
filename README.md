Requirements
---
 - Docker

How to run?
---
 - docker-compose up --build
 - visit localhost:8080
 - TODO endpoint for scrapper

 Localy
 ---
 - Move into scrappers dir
 - scrapy runspider {scarrper}.py

How to use?
---
 - create functions that do the scraping
 - import and use them in server.py
 - add routes to to the usages
 - profit

Misc
---
 - On windows might be needed: pip install pypiwin32

Limitations
 - Can't get VIN/Registration/Phone/E-mail as those are AJAX calls

Final thoughts
 - Should use selenium or similar