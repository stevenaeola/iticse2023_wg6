
inst_scrape :=  Durham_England Edinburgh_Scotland Glasgow_Scotland Uppsala_Sweden
inst_pre := CAUKiel_Germany Kennesaw_USA UofT_Canada UOC_Spain VirginiaTech_USA
inst_todo := SDSU_USA
inst_all := $(inst_scrape) $(inst_pre) $(inst_todo)

scrape_csvs := $(foreach inst,$(inst_scrape),$(inst)/electives_scraped.csv)
pre_csvs := $(foreach inst,$(inst_pre),$(inst)/electives_pre.csv)

python_scrape := scraping.py


all: inst_scrape inst_pre

inst_scrape: $(inst_scrape)
inst_pre: $(inst_pre)


Durham_England: Durham_England/electives_scraped.csv
Glasgow_Scotland: Glasgow_Scotland/electives_scraped.csv 
Edinburgh_Scotland: Edinburgh_Scotland/electives_scraped.csv 
Uppsala_Sweden: Uppsala_Sweden/electives_scraped.csv 

Durham_England/electives_scraped.csv: Durham_England/institution.json $(python_scrape)
	python3 $(python_scrape) $(@D)

Glasgow_Scotland/electives_scraped.csv: Glasgow_Scotland/institution.json $(python_scrape)
	python3 $(python_scrape) $(@D)

Edinburgh_Scotland/electives_scraped.csv: Edinburgh_Scotland/institution.json $(python_scrape)
	python3 $(python_scrape) $(@D)

Uppsala_Sweden/electives_scraped.csv: Uppsala_Sweden/institution.json $(python_scrape)
	python3 $(python_scrape) $(@D)

#$(scrape_csvs): $@/institution.json $(python_scrape)
#	python3 $(python_scrape) $(@D)

$(pre_csvs): $(@D)/institution.json scraping.py


