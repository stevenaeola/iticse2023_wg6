data {
    int<lower=1> COHORTS;
    array[COHORTS] int<lower=0> cohort_women;
    array[COHORTS] int<lower=0> cohort_men;
    array[COHORTS] real<lower=0> mu_modules_taken;
    
    // number of TOPICS including ACM curriculum areas and CAH application areas
    int<lower=1> TOPICS;
    // Maximum number of modules available per cohort
    int<lower=1> MAXMODULES;

    // actual number of elective modules per cohort
    array[COHORTS] int<lower=0> MODULES;
    // mapping of topics to modules. Where there are multiple coders it could be either 0/1 (OR) or 0/1/2 etc (PLUS)
    array[COHORTS] matrix<lower=0>[MAXMODULES,TOPICS] module_topics;
    array[COHORTS,MAXMODULES] real<lower=0> module_min_students;
    array[COHORTS,MAXMODULES] real<lower=0> module_max_students;
    array[COHORTS,MAXMODULES] int<lower=0> module_women;
    array[COHORTS,MAXMODULES] int<lower=0> module_men;
}

transformed data {
// constants
    int ideal_mu = 1000;
    int ideal_sigma = 200;
    real epsilon_sigma = 0.001;
// derived values
    array[COHORTS] real<lower=0> expected_modules_women;
    array[COHORTS] real<lower=0> expected_modules_men;
    for(cohort in 1:COHORTS){
        expected_modules_women[cohort] = mu_modules_taken[cohort] * cohort_women[cohort];
        expected_modules_men[cohort] = mu_modules_taken[cohort] * cohort_men[cohort];
    }
}

parameters {
    real<lower=epsilon_sigma> sigma_topic_all;
    real<lower=epsilon_sigma> sigma_topic_women_men_diff;
    real<lower=epsilon_sigma> sigma_nontopic_women;
    real<lower=epsilon_sigma> sigma_nontopic_men;
    vector[TOPICS] popularity_topic_all;
    /* popularity_topic_women_men_diff will be added (.5x) to women, subtracted (0.5x) from men */
    vector[TOPICS] popularity_topic_women_men_diff;

    array[COHORTS] vector[MAXMODULES] popularity_module_non_topic_women;
    array[COHORTS] vector[MAXMODULES] popularity_module_non_topic_men;
}
transformed parameters {



}

model {
// https://discourse.mc-stan.org/t/rejecting-initial-value-chain-1-log-probability-evaluates-to-log-0-i-e-negative-infinity/17866/3

    sigma_topic_all ~ exponential(1.0/ideal_sigma);
    sigma_topic_women_men_diff ~ exponential(1.0/ideal_sigma);
    sigma_nontopic_men ~ exponential(1.0/ideal_sigma);
    sigma_nontopic_women ~ exponential(1.0/ideal_sigma);

//vectorised over TOPICS
    popularity_topic_all ~ normal(0, sigma_topic_all);
    popularity_topic_women_men_diff ~ normal(0, sigma_topic_women_men_diff);

// vectorised over COHORTS


    array[COHORTS] vector[MAXMODULES] popularity_module_topic_all;
    array[COHORTS] vector[MAXMODULES] popularity_module_topic_women_men_diff;
    array[COHORTS] vector[MAXMODULES] popularity_module_topic_women;
    array[COHORTS] vector[MAXMODULES] popularity_module_topic_men;

    array[COHORTS] vector[MAXMODULES] popularity_module_women;
    array[COHORTS] vector[MAXMODULES] popularity_module_men;


    for(cohort in 1:COHORTS){
        popularity_module_topic_all[cohort] = module_topics[cohort] * popularity_topic_all;
        popularity_module_topic_women_men_diff[cohort] = module_topics[cohort] * popularity_topic_women_men_diff;
        popularity_module_topic_women[cohort] = popularity_module_topic_all[cohort] + 0.5*popularity_module_topic_women_men_diff[cohort];
        popularity_module_topic_men[cohort] = popularity_module_topic_all[cohort] - 0.5*popularity_module_topic_women_men_diff[cohort];
        popularity_module_non_topic_women[cohort] ~ normal(0, sigma_nontopic_women);
        popularity_module_non_topic_men[cohort] ~ normal(0, sigma_nontopic_men);
        popularity_module_women[cohort] = ideal_mu + popularity_module_topic_women[cohort] + popularity_module_non_topic_women[cohort];
        popularity_module_men[cohort] = ideal_mu + popularity_module_topic_men[cohort] + popularity_module_non_topic_men[cohort];
        int n_modules = MODULES[cohort];
//        print ("cohort ", cohort, " MAXMODULES ", MAXMODULES, "n_modules", n_modules);
        vector[n_modules] rate_women_relative;
        vector[n_modules] rate_men_relative;
        vector[n_modules] rate_women;
        vector[n_modules] rate_men;
        for(m in 1:n_modules){
            rate_women_relative[m] = pow(10,(popularity_module_women[cohort][m])*(-1.0/400));
            rate_men_relative[m] = pow(10,(popularity_module_men[cohort][m])*(-1.0/400));
        }
        // do it again, now the rate_relative vectors are complete so we can find the norm
        for(m in 1:n_modules){
            // TODO change rate for upper cap in module_max_students
            rate_women[m] = (1.0/ norm1(rate_women_relative)) * rate_women_relative[m] * expected_modules_women[cohort];
            rate_men[m] = (1.0/ norm1(rate_men_relative)) * rate_men_relative[m] * expected_modules_men[cohort];
            if(rate_women[m]<0.000001){
                rate_women[m] = 0.000001;
            }
            if(rate_men[m]<0.000001){
                rate_men[m] = 0.000001;
            }
            // TODO apply bounds for upper and lower cap in module_min_students and module_max_students    
            module_women[cohort,m] ~ poisson(1.0/rate_women[m]);
            module_men[cohort,m] ~ poisson(1.0/rate_men[m]);
        }
    }

}



