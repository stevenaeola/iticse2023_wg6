import pandas as pd

fit = pd.read_csv("results/stansummary-wg6_config.json-seed-1-samples-500.csv")
topics = range(39)
results = []

for topic in topics:
    topic_text = "popularity_topic_all\[" + str(topic) + "\]"
    fit_topic_all = fit[fit['variable'].str.contains(topic_text)].iloc[0]['mean']
    topic_text = "popularity_topic_women_men_diff\[" + str(topic) + "\]"
    fit_topic_diff = fit[fit['variable'].str.contains(topic_text)].iloc[0]['mean']
    results.append({"topic": topic, "AllEst": fit_topic_all, "WomenMenEst": fit_topic_diff})

analysis_df = pd.DataFrame(results)
print(analysis_df)


