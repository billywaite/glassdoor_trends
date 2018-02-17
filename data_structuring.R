
library(tidyr)
library(dplyr)

setwd("/Users/wwaite/Dev/Python/scraping_glassdoor/scraped_data")

# Combine all scraped csvs into 1 df
df <- tbl_df(do.call(rbind, lapply(list.files(), read.csv)))

# Load file with full company name + ticker
tickers <- read.csv("wilshire5000_gd.csv")

# Join tickers + full name to main df
df <- df %>%
  full_join(tickers, by = c("company_name" = "company_short_name"))

# Convert milliseconds to date
df$date <- as.POSIXct(df$date/1000, origin="1970-01-01")
df$full_company_name <- as.character(df$full_company_name)
df$ticker <- as.character(df$ticker)

# Clean up df
long_df <- df %>%
  rename("company_short_name" = "company_name") %>%
  select("full_company_name", "company_short_name", "ticker",
         "date", "rating_category", "rating") %>%
  distinct()

# Write long data format
write.csv(clean_df, "long_format_historicals.csv")

# Spread data on rating category
spread_df <- clean_df %>%
  spread(rating_category, rating) %>%
  select(1:13)

# Write wide format
write.csv(spread_df, "wide_format_historicals.csv")
