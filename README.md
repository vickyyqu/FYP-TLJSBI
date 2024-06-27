# ApplianceAllStar
SMU FYP with TLJ Home Solutions

## webcrawltlj folder
Folder contains the scrapy web scrawlers that will be used for the multiple e-commerce web crawling

## New Spider Crawler creation
Go into spiders directory
- cd webcrawltlj/webcrawltlj/spiders
- scrapy genspider [insert spider name] [https://www.example.com]

## Running your Spider Crawler
In the spider directory, run
- scrapy crawl [spider name] -o output/date_[json name].json -t json 

"scrapy crawl [spider name]" runs the crawler through the list of urls specified in "start_urls"

"-o output/[json name].json" puts your data output in a json file in the new folder output
"-t json" forces the cmd line to strictly follow instructions stated

## for settings.py
- go to file settings.py
- under FEEDS, add the following template
- '[json name].json': {
        'format': 'json',
        'overwrite': True, 
    },
- Unsure if overwrite False will change anything, but leaving it as false in the meantime

## Git branching
For now just create a branch with your name, purpose of branching and maybe the website

eg johncena_scraper_qoo10

Later we'll figure out the git stuff once finals are over

## Misc
- Can try beautifulsoup, its a bit easier (subjective)
- Try to use selenium wait time with the scrapers to ensure we don't get IP blocked
- The scraper for TLJ's website is not really working, can refer but don't rely : )
  
err if anything just text in grp,, edit read me as you see fit,, okie gn

Last updated: 22/12/23
