
inst_scrape :=  Durham_England Edinburgh_Scotland Glasgow_Scotland Uppsala_Sweden
inst_pre := CAUKiel_Germany Kennesaw_USA UofT_Canada UOC_Spain VirginiaTech_USA
inst_todo := SDSU_USA
inst_all := $(inst_scrape) $(inst_pre) $(inst_todo)

scraped_file := electives_scraped.csv
scrape_csvs := $(foreach inst,$(inst_scrape),$(inst)/$(scraped_file))

pre_file := electives_pre.csv
pre_in_file := electives_in.csv
pre_csvs := $(foreach inst,$(inst_pre),$(inst)/$(pre_file))

python_scrape := scraping.py
python_wrangle := pre_wrangling.py

all: inst_scrape inst_pre

inst_scrape: $(inst_scrape)
inst_pre: $(inst_pre)


Durham_England: Durham_England/$(scraped_file)
Glasgow_Scotland: Glasgow_Scotland/$(scraped_file)
Edinburgh_Scotland: Edinburgh_Scotland/$(scraped_file)
Uppsala_Sweden: Uppsala_Sweden/$(scraped_file) 

Durham_England/$(scraped_file): Durham_England/institution.json $(python_scrape)
	python3 $(python_scrape) $(@D)

Glasgow_Scotland/$(scraped_file): Glasgow_Scotland/institution.json $(python_scrape)
	python3 $(python_scrape) $(@D)

Edinburgh_Scotland/$(scraped_file): Edinburgh_Scotland/institution.json $(python_scrape)
	python3 $(python_scrape) $(@D)

Uppsala_Sweden/$(scraped_file): Uppsala_Sweden/institution.json $(python_scrape)
	python3 $(python_scrape) $(@D)

CAUKiel_Germany: CAUKiel_Germany/$(pre_file)
Kennesaw_USA: Kennesaw_USA/$(pre_file)
VirginiaTech_USA: VirginiaTech_USA/$(pre_file)


CAUKiel_Germany/$(pre_file): CAUKiel_Germany/institution.json CAUKiel_Germany/$(pre_in_file) $(python_wrangle)
	python3 $(python_wrangle) $(@D)

Kennesaw_USA/$(pre_file): Kennesaw_USA/institution.json Kennesaw_USA/$(pre_in_file) $(python_wrangle)
	python3 $(python_wrangle) $(@D)

VirginiaTech_USA/$(pre_file): VirginiaTech_USA/institution.json VirginiaTech_USA/$(pre_in_file) $(python_wrangle)
	python3 $(python_wrangle) $(@D)
