import re
import pandas as pdf
from pandas.io.json import json_normalize 
import json


# This method is used to convert two JSON files into a Pandas dataframe.
def fetch_yelp_reviews(reviews_file):
    yelp = None
    with open(reviews_file) as in_file:
        raw = pd.read_json(in_file)
        reviews = raw["reviews"]
        yelp = json_normalize(reviews)
     
    return yelp

def fetch_yelp_businesses(businesses_file):
    yelp = None
    with open(businesses_file) as in_file:
        raw = pd.read_json(in_file)
        businesses = raw["businesses"]
        yelp = json_normalize(businesses)
 
    return yelp


# This function lists businesses, reviews with specific star
def q1_yelp(businesses,reviews):
    by_stars(businesses, reviews, 5.0)
    by_stars(businesses, reviews, 4.5)
    by_stars(businesses, reviews, 4.0)
    by_stars(businesses, reviews, 3.5)
    by_stars(businesses, reviews, 3.0)
    by_stars(businesses, reviews, 2.5)
    by_stars(businesses, reviews, 2.0)
    by_stars(businesses, reviews, 1.5)
    by_stars(businesses, reviews, 1.0)

# This function is used to find number of restaurant and mean number of reviews' words counting by star
def by_stars(businesses, reviews, stars):
    rows = businesses.shape[0]
    
    businesses_by_stars = businesses.loc[businesses.star_count == stars]
    num_businesses_by_stars = businesses_by_stars.shape[0]

    reviews_by_stars = reviews.loc[reviews.stars == stars]
    reviews_by_stars["review_len"] = reviews_by_stars["text"].apply(word_count)
    review_word_count = reviews_by_stars["review_len"].mean()
    
    print(f"stars {stars}, percentage: {(num_businesses_by_stars/rows*100):.2f}%, mean word count {review_word_count}")

# This function is used to count the number of words in each reviews.    
def word_count(str1):
    total = 1
    for i in range(len(str1)):
        if(str1[i] == ' ' or str1[i] == '\n' or str1[i] == '\t'):
            total = total + 1
    return total

# This function is to analyze restuarants in terms of regions by ZIP codes
def q2_yelp(businesses, reviews):
    
    # explore the amount of restuarants in each regions and turn out to find:
      # 0 in Philadelphia (19xxx); 1 in others (16xxx, 17xxx, 18xxx);4227 in Pittsburgh (15xxx);9 unknown (no zip code)
    groupby_city = businesses.groupby("city_from_zip")
    print("Number of businesses by city:")
    print(groupby_city.size())

    # create two new variables to save businesses in "Other" regions and "Unrecognized" regions
    others_business_ids = businesses.loc[businesses.city_from_zip == "Others"].loc[:, "business_id"].values
    unrecognized_business_ids = businesses.loc[businesses.city_from_zip == "Unrecognized"].loc[:, "business_id"].values
    
    # analyze reviews by each region 
    reviews["city_from_zip"] = reviews["business_id"].apply(lambda x: find_zip_from_bussiness_id(x, others_business_ids, unrecognized_business_ids))
    groupby_city = reviews.groupby("city_from_zip")
    print("Reviews by regions: Number of reviews & mean score of reviews")
    star_statistics(reviews, "city_from_zip")

# This function is using regular express to find businesses in each regions     
def city_from_zip(zip_code):
    regex_zip_philadelphia = re.compile(r"19\d{3}")
    regex_zip_pittsburgh = re.compile(r"15\d{3}")
    regex_zip_others = re.compile(r"(16|17|18)\d{3}")
    if re.search(regex_zip_philadelphia, zip_code):
        return "Phiadelphia"
    elif re.search(regex_zip_pittsburgh, zip_code):
        return "Pittsburgh"
    elif re.search(regex_zip_others, zip_code):
        return "Others"
    else:
        return "Unrecognized"

# This function is used to classify regions
def find_zip_from_bussiness_id(business_id, others_business_ids, unrecognized_business_ids):
    if business_id in others_business_ids:
        return "Others"
    elif business_id in unrecognized_business_ids:
        return "Unrecognized"
    else:
        return "Pittsburgh" # Directly went to Pittsburge since business in Philly is zero.

# This function is used to create a df to exhibit results
def star_statistics(df, col):
    subgroup_stars = df.groupby(col)["stars"]
    subgroup_statistics = subgroup_stars.agg(["size", "mean"])
    print(subgroup_statistics)

# This function is used to screen and compare positive reviews and negative reviews
def q3_yelp(review):
    positive_words = "(good|great|amazing|delicious|fabulous|delightful|enjoyable|satisfying|pleasant|lovely)"
    negative_words = "(bad|terrible|poor|disgusting|gross|rude|horrible|awful|dirty|sad)"

    not_prefix = "[^(not)]\s" 
    positive_pattern = re.compile(f"{not_prefix}{positive_words}")
    negative_pattern = re.compile(f"{not_prefix}{negative_words}")
    # With "not prefix" syntax, we can avoid 5246 false positives and 2614 false negatives.

    positive_mentions = re.findall(positive_pattern, review)
    negative_mentions = re.findall(negative_pattern, review)

    if len(positive_mentions) > len(negative_mentions):
        return "Positive"
    elif len(negative_mentions) > len(positive_mentions):
        return "Negative"
    else:
        return "Unknown"

if __name__ == "__main__":
    businesses_file = "PA_businesses.json"
    businesses = fetch_yelp_businesses(businesses_file)

    reviews_file = "PA_reviews_full.json"
    reviews = fetch_yelp_reviews(reviews_file)

    print("-----Q1-----")
    businesses["star_count"] = businesses.loc[:, "stars"]
    q1_yelp(businesses, reviews)

    print("-----Q2-----")
    businesses["city_from_zip"] = businesses["postal_code"].apply(city_from_zip)
    q2_yelp(businesses, reviews)

    print("-----Q3-----")
    group_means = businesses.groupby("stars").mean()
    print(f"stars: average number of reviews")
    for group in group_means.index.unique():
        review_count = group_means.loc[group, "review_count"]
        print(f"   {group}: {review_count:.2f}")
    reviews["sentiment"] = reviews.loc[:, "text"].apply(q3_yelp)
    star_statistics(reviews, "sentiment")
