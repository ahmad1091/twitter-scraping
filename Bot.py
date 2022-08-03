from os import stat
from secret import accounts
import tweepy as ty
import time
from datetime import datetime, timedelta, timezone
import sys
from urllib import request, parse
import json
import random
import xlwt
import xlsxwriter
import xlrd


user_names = ["Humour_lesss","IamRamishAsghar"]
#All Pakistan Filter
location = ["Pakistan", "Multan, Pakistan", "Islamabad, Pakistan", "Karachi, Pakistan", "Lahore, Pakistan", "Peshawar, Pakistan", "Jehlum", "Jehlum, Pakistan", "Punjab, Pakistan", "Sindh, Pakistan", "Multan", "Karachi", "Islamabad", "KPK", "Lahore", "Rawalpindi", "Rawalpindi, Pakistan", "اسلام آباد، پاکستان" ,"اسلام آباد", "راولپنڈی", "راولپنڈی، پاکستان", "کراچی، پاکستان", "لاہور، پاکستان", "پشاور", "پاکستان", "پشاور", "ملتان، پاکستان", "پنجاب" ,"پنجاب، پاکستان", "جہلم، پاکستان" ,"جہلم", "سندھ، پاکستان", "ملتان", "لاہور" ,"کراچی"]
# Islamabad Only Filters
# ["Islamabad", "Islamabad, Pakistan", "Capital", "Capital Territory", "Capital Territory, Pakistan", "Rawalpindi", "Rawalpindi, Pakistan"]

#Pakistan Filters
#["Pakistan", "Multan, Pakistan", "Islamabad, Pakistan", "Karachi, Pakistan", "Lahore, Pakistan", "Peshawar, Pakistan", "Jehlum", "Jehlum, Pakistan", "Punjab, Pakistan", "Sindh, Pakistan", "Multan", "Karachi", "Islamabad", "KPK", "Lahore", "Rawalpindi", "Rawalpindi, Pakistan", "اسلام آباد، پاکستان" ,"اسلام آباد", "راولپنڈی", "راولپنڈی، پاکستان", "کراچی، پاکستان", "لاہور، پاکستان", "پشاور", "پاکستان", "پشاور", "ملتان، پاکستان", "پنجاب" ,"پنجاب، پاکستان", "جہلم، پاکستان" ,"جہلم", "سندھ، پاکستان", "ملتان", "لاہور" ,"کراچی"]

option = 1
count = 8000
#################################################### FUNCTIONS ###########################################################

def set_twitter_auth(credentials):

    CONSUMER_KEY = credentials['CONSUMER_KEY']
    CONSUMER_SECRET = credentials['CONSUMER_SECRET']
    ACCESS_TOKEN = credentials['ACCESS_TOKEN']
    ACCESS_SECRET = credentials['ACCESS_SECRET']
    # auth = ty.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    # auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    auth = ty.OAuth1UserHandler(
   CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET
    )
    api = ty.API(auth ,wait_on_rate_limit=True, retry_count=10, retry_delay=900, retry_errors=5)
    print('Credentials Verified')
    return api


def get_user_followers(api, screen_name):
    ids = []
    counting = 0
    for page in ty.Cursor(api.get_follower_ids, screen_name=screen_name).pages():
        counting += 1
        ids.extend(page)
        time.sleep(1)
        print(counting)
        if counting == 5:
            counting = 0
            break
    print('IDS fetched')
    return ids


def get_user_friends(api, screen_name):
    friends = api.get_friend_ids(screen_name=screen_name)
    return friends


def get_last_tweet(api, user,ids_chunk):
    users_chunk = api.lookup_users(ids_chunk)
    return users_chunk


def get_previous_followed(file_name):
    fetched_list = []
    with open(file_name) as my_file:
        for line in my_file:
            fetched_list.append(line.rstrip('\n'))
    return fetched_list


def enter_in_record(username,file_name):
    file = open(file_name, 'a')
    username = str(username)
    file.write(username)
    file.write('\n')
    file.close()
    print(username, 'Entered in file')


def user_follow(api,id):
        try:
            print(123)
            api.create_friendship(user_id=id)
            print('Followed user', api.get_user(user_id=id).screen_name, 'after all filter checks....!!! ')
        except Exception as e:
            print(321)
            print(e)


def unfollow_user(api,id):
    try:
        api.destroy_friendship(user_id=id)
    except Exception as e:
        print(e)

def custom_delay(delay_value):
    print('Delay of ', delay_value, 'seconds starting')
    for i in range(delay_value):
        time.sleep(1)
        print(i, ' seconds passed')


def distraction(api):
    try:
        api.rate_limit_status()
    except Exception as e:
        print(e.response.json())
        custom_delay(420)
    try:
        top_trends = api.trends_available()
    except Exception as e:
        print(e)
    print('Top Trends Today:\n\n', top_trends)


# def create_excel_sheet(fav_tweets_ids_array):
#     book = xlwt.Workbook()
#     sheet = book.add_sheet('Sheet 1')
#     headings = fav_tweets_ids_array.keys()
#     for i in len(fav_tweets_ids_array):
#
#     book.save('fav_tweets_in_xls.xls')


def menu():
    menu_string = """Welcome to My Custom Bot\n\nPlease select from the following menu\n\n
    Press 1 to follow a user from all your accounts\n
    Press 2 to follow users who tweeted specific keyword\n
    Press 3 to Follow profiles that are following your profiles\n
    Press 4 to Follow profiles that are following a specific profile\n
    Press 5 to Unfollow a specific profile with all your accounts\n
    Press 6 to Unfollow profiles that are following your profiles\n
    Press 7 to Unfollow profiles you are following\n
    Press 8 to Unfollow profiles that are not following you back\n
    Press 9 to  Clear your favorites\n
    Press 10 to Exclude specific profiles from following or un following\n
    Press 11 to Unfollow actions(Your Custom Filter)\n
    Press 12 to Follow Actions(Your Custom Filter)\n
    Press 13 to Block Account of a user from all your accounts\n
    Press 14 to Follow profiles in the (following) of a specific profile\n
    Press 15 to Follow (Followers) of the followers of a specific profile\n
    Press 16 to Follow (Followers) of the (following) of a specific profile\n
    Press 0 to exit Bot\n\n\n
    """
    selection = input(menu_string)
    return selection


def process_selection(selection):
    if int(selection) == 0:
        sys.exit(0)
    if int(selection) == 1:
        screen_name_to_follow= input("Enter the username to follow: ")
        if check_blacklist(screen_name_to_follow):
            print("User is present in blacklist. Cannot Follow User")
        else:
            follow_specific_acc_from_all_acc(accounts, screen_name_to_follow)
    elif int(selection) == 2:
        hashtag = input("Enter the hashtag or keyword you want to use to follow: ")
        fetch_hashtag_tweets(accounts, hashtag)
    elif int(selection) == 3:
        follow_followers(accounts)
    elif int(selection) == 4:
        user_name_for_followers = input("Enter the username to get his followers: ")
        follow_followers_of_someone(accounts, user_name_for_followers)
    elif int(selection) == 5:
        screen_name_to_unfollow = input("Enter the username to unfollow: ")
        if check_whitelist(screen_name_to_unfollow):
            print("User is present in Whitelist. Cannot UnFollow User")
        else:
            Unfollow_specific_acc_from_all_acc(accounts, screen_name_to_unfollow)
    elif int(selection) == 6:
        unfollow_non_followers(accounts)
    elif int(selection) == 7:
        unfollow_all(accounts)
    elif int(selection) == 8:
        unfollow_non_follow_backs(accounts)
    elif int(selection) == 9:
        clear_favorites(accounts)
    elif int(selection) == 10:
        sub_selection = input("Press 1 to enter in Whitelist(Never Unfollow)\n\nPress 2 to enter user in Blacklist(Never Follow)\n\n")
        if int(sub_selection) == 1:
            username = input("You have selected Whitelist\n\nPlease enter username to add to Whitelist\n\n")
            whitelist(username)
        elif int(sub_selection) == 2:
            username = input("You have selected Blacklist\n\nPlease enter username to add to Blacklist\n\n")
            blacklist(username)
        else:
            print("You have entered wrong choice")
    elif int(selection) == 11:
        sub_selection = input("""Select form following filters\n\n
                                Press 1 to Unfollow Users not Following Back\n\n
                                Press 2 to Unfollow Users without AVI\n\n
                                Press 3 to Unfollow Inactive Users\n\n\n
                                Press 4 to Unfollow Fake Users\n\n\n""")
        unfollow_actions(accounts, sub_selection)
    elif int(selection) == 12:
        print("Follow Criteria Met")
    elif int(selection) == 13:
        user_to_block = input("Enter username to block: ")
        for account in accounts:
            api = set_twitter_auth(account)
            user = api.get_user(screen_name=account['USER_NAME'])
            screen_name = user.screen_name
            block_user(api,user_to_block)
    elif int(selection) == 14:
        user_name_for_followers = input("Enter the username to get his following: ")
        follow_following_of_someone(accounts, user_name_for_followers)
    elif int(selection) == 15:
        user_name_for_followers = input("Enter the username to get his followers: ")
        follow_followers_of_following_of_someone(accounts, user_name_for_followers)
    elif int(selection) == 16:
        user_name_for_followers = input("Enter the username to get his following: ")
        follow_following_of_following_of_someone(accounts, user_name_for_followers)

################################################### FUNCTIONS END ######################################################

##               THESE FILTERS MAKE THE BOT TO PERFORM TWITTER OPERATIONS WITH USER SPECIFIED CONDITIONS              ##
        
################################################### FILTERS ############################################################


def write_to_json(file_name,json_object):
    with open(file_name, 'w+') as f:
        json.dump(json_object, f)

def tweet_to_xlsx(file_name,tweet):
    tweet_list = []
    tweet_list.append(tweet)
  # tweet_list.append(tweet.text)
    file_name = 'Favourite_tweet' + str(random.randint(0,100)) +'.xlsx'
    print(file_name)
    workbook = xlsxwriter.Workbook()
    worksheet = workbook.add_worksheet()
    row = find_excel_length(file_name) + 1
    print("Row Number: ", row)
    col = 0
    for tweet_created_at, tweet_id, tweet_text, created_by in tweet_list:
        worksheet.write(row, col, tweet_created_at)
        worksheet.write(row, col + 1, tweet_id)
        worksheet.write(row, col + 2, tweet_text)
        worksheet.write(row, col + 3, created_by)

    workbook.close()

def find_excel_length(file_name):
    book = xlrd.open_workbook(file_name)
    sheet = book.sheet_by_index(0)

    row_count = sheet.nrows
    # for row in range(sheet.nrows):
    #     for col in sheet.row_values(row):
    #         if col.strip() != '':
    #             count += 1
    return row_count

def dp_check(follow_user):
    filter_status = True
    print('follow_user.default_profile_image:',follow_user.default_profile_image)
    print('follow_user.profile_image_url:',follow_user.profile_image_url)
    try:
        if follow_user.default_profile_image:
            filter_status = False
            print(follow_user.screen_name, 'has avatar')
    except Exception as e:
        print(e)
    return filter_status


def followers_count(follow_user, count):
    filter_status = False
    if follow_user.followers_count < count:
        filter_status = True
        print(follow_user.screen_name, 'has followers less than', count)
    return filter_status


def location_check(follow_user, location):
    filter_status = False
    if follow_user.location in location:
        filter_status = True
        print(follow_user.screen_name, 'Location Matched')
    return filter_status


def friend_or_follower(follow_user, api, own_friends_ids, own_followers_ids):
    filter_status = False
    test_id = follow_user.id
    print(follow_user.id)
    if (follow_user.id not in own_followers_ids) & (follow_user.id not in own_friends_ids):
        filter_status = True
        print(follow_user.screen_name, 'is not a Friend or Follower')
    return filter_status


def last_tweeted(follow_user):
    filter_status = False
    try:
        tweet = follow_user.status.created_at
        # print('datetime.today()-tweet', datetime.today().replace(tzinfo=timezone.utc) , tweet)
        if(datetime.today().replace(tzinfo=timezone.utc)-tweet).days < 1:
            filter_status = True
            print(follow_user.screen_name, 'has recent tweet')
    except Exception as e:
        print(e)
    return filter_status


def filters(follow_user, api, own_friends, own_follower_ids):
    all_filters = False
    dp_filter = dp_check(follow_user)
    followers_count_filter = followers_count(follow_user, count)
    location_check_filter = location_check(follow_user, location)
    friend_or_follower_filter = friend_or_follower(follow_user, api, own_friends, own_follower_ids)
    last_tweeted_filter = last_tweeted(follow_user)

    if dp_filter & followers_count_filter & location_check_filter & friend_or_follower_filter & last_tweeted_filter:
        all_filters = True
        print('All filters applied for the user: ', follow_user.screen_name)
        print('\u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713 \u2713')
    return all_filters


#################################################### END OF FILTERS ##################################################


################################################## AMMAR FILTERS ###########################################################

# Follow a specific profile with all your accounts
def follow_specific_acc_from_all_acc(account_array, screen_name_to_follow):
    # Authentication
    for account in account_array:
        follow_count = 0
        api = set_twitter_auth(account)
        #follow_user = api.get_user(screen_name_to_follow)
        user_id = api.get_user(screen_name=screen_name_to_follow).id
        if check_blacklist_id(user_id):
            print("User is in Blacklist. Cannot Follow")
        else:
            user_follow(api, user_id)
            follow_count += 1
            print("Followed user from: ", api.get_user(screen_name=account['USER_NAME']).screen_name)
            if follow_count >= 500:
                print("Followed 500 people. It is safe")
                follow_count = 0
                break

#Follow profiles that posted recently using a specific keywords/Hashtags
def fetch_hashtag_tweets(account_array, hashtag): #
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        print(user.screen_name)
        screen_name = user.screen_name
        #Getting recent 100 tweeets of the keyword or hashtag
        hashtag_tweets = api.search_tweets(q=hashtag,lang="en")
        count = 0

        #Getting users of tweets and following them one by one
        total_file = account['FILE_NAME']
        today_file = account['LOG_FILE']
        for tweet in hashtag_tweets:
            count = count + 1
            user = tweet.author
            if check_blacklist(user.screen_name):
                print(user.screen_name, " is in blacklist. Cannot Follow")
            else:
                user_follow(api, user.id)
                enter_in_record(user.screen_name,total_file)
                enter_in_record(user.id,today_file)
                print("Followed ", count, "users from account: ", screen_name)


#Follow profiles that are following your profiles
def follow_followers(account_array):
    #Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name =  user.screen_name
        user_id = user.id

        #Getting Following and followers
        followers_ids = get_user_followers(api, screen_name)
        following_ids = get_user_friends(api, screen_name)

        #Following all followers
        for follower_id in followers_ids:
            count = 0
            if follower_id not in following_ids:
                if check_blacklist(screen_name) | check_blacklist_id(user_id):
                    print(screen_name, " is in blacklist. Cannot Follow")
                else:
                    user_follow(api, follower_id)
                    count = count + 1
        print("Followed ",count, "users from account: ", screen_name)


#Follow profiles that are following a specific profile
def follow_followers_of_someone(account_array,user_name_for_followers):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name = user.screen_name
        user_id = user.id

        # Getting own Following and followers
        followers_ids = get_user_followers(api, screen_name)
        following_ids = get_user_friends(api, screen_name)

        # Getting followers of desired user
        user_followers_ids = get_user_followers(api, user_name_for_followers)

        for user_follower_id in user_followers_ids:
            count = 0
            if user_follower_id not in following_ids:
                if check_blacklist(screen_name) | check_blacklist_id(user_id):
                    print(screen_name, " is in blacklist. Cannot Follow")
                else:
                    user_follow(api, user_follower_id)
                    count = count + 1
        print("Followed ",count, "users from account: ", screen_name)


# Unfollow a specific profile with all your accounts
def Unfollow_specific_acc_from_all_acc(account_array, screen_name_to_unfollow):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        follow_user = api.get_user(screen_name=screen_name_to_unfollow)
        if check_whitelist_id(follow_user.id):
            print("Whitelist User!!! Cannot Unfollow: ", screen_name_to_unfollow )
        else:
            unfollow_user(api, follow_user.id)
            print("Unfollowed", screen_name_to_unfollow, "from: " , api.get_user(screen_name=account['USER_NAME']).screen_name)


#Unfollow profiles that are following your profiles
def unfollow_non_followers(account_array):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name = user.screen_name
        user_id = user.id

        # Getting own Following and followers
        followers_ids = get_user_followers(api, screen_name)
        following_ids = get_user_friends(api, screen_name)
        print(followers_ids,following_ids)
        #Unfollowing Followers
        for friend in following_ids:
            userName =api.get_user(user_id=friend).screen_name
            print(check_whitelist(userName) )
            if friend in followers_ids:
                if check_whitelist(userName):
                    print("User In whitelist. Cannot Unfollow" , screen_name)
                else:
                    unfollow_user(api, friend)
                    custom_delay(180)


#Unfollow profiles you are following
def unfollow_all(account_array):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name = user.screen_name

        # Getting own Following and followers
        following_ids = get_user_friends(api, screen_name)
        count = 0
        for friend in following_ids:
            if count < 5000:
                unfollow_user(api, friend)
                custom_delay(3)
                count = count + 1
                print ("Unfollowing: ",api.get_user(user_id=friend).screen_name, " using Bot\n", count, " users unfollowed")
        print("Unfollowed: ",count , "users")

#Unfollow profiles that are not following you back
def unfollow_non_follow_backs(account_array):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name = user.screen_name

        # Getting own Following and followers
        followers_ids = get_user_followers(api, screen_name)
        following_ids = get_user_friends(api, screen_name)
        count = 0
        followers = []
        following = []
        #Gathering Followers in an array
        for follower in followers_ids:
            followers.append(follower)

        for friend in following_ids:
            following.append(friend)

        non_followers = list(set(following)-set(followers))
        print(len(non_followers),' people in your following are not your followers')

        for non_follower in non_followers:
            userName =api.get_user(user_id=non_follower).screen_name
            if count <= 5000:
                if check_whitelist(userName):
                        print("User In whitelist. Cannot Unfollow" , api.get_user(user_id=non_follower).screen_name)
                else:
                    unfollow_user(api, non_follower)
                    custom_delay(3)
                    count = count + 1
                    print("unfollowed", api.get_user(user_id = non_follower).screen_name)
            print("Unfollowerd: ", count, " users")


#Clear your favorites but first export all data to be downloaded as xls file , then delete it
def clear_favorites(account_array):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name = user.screen_name
        #Geting Favorites
        favourites = []
        favorite_ids = api.get_favorites(screen_name=screen_name)
        for fav_id in favorite_ids:
            fav_tweet = fav_id._json
            tweet_created_at = fav_tweet['created_at']
            tweet_id = fav_tweet['id']
            tweet_text = fav_tweet['text']
            user = fav_tweet['user']
            created_by = user['screen_name']
            favourites.append({
                'text': tweet_text,
                'author_name': created_by,
                'created_at' : tweet_created_at,
                'tweet_id':tweet_id
            })
            # values_array = [tweet_created_at , tweet_id , tweet_text , created_by]
            # tweet_to_xlsx('favourite_tweets.xlsx', values_array)
            api.destroy_favorite(tweet_id)
            print("Following tweet is written to Excel\nCreated at: ",tweet_created_at,"\nTweet ID: ", tweet_id, "\nTweet Text: ", tweet_text, "\nClearing Favourite........\n\n\nDone")
        write_to_json('favourites.json', favourites)

# Exclude specific profiles from following or un following
def whitelist(username):
    enter_in_record(username, 'whitelist.txt')


def check_whitelist(username):
    print('Check the white list for : ',username)
    status = False
    whitelist = get_previous_followed('whitelist.txt')
    if username in whitelist:
        status = True
    return status


def blacklist(username):
    enter_in_record(username, 'blacklist.txt')


def check_blacklist(username):
    status = False
    blacklist = get_previous_followed('blacklist.txt')
    if username in blacklist:
        status = True
    return status


def check_blacklist_id(user_id):
    status = False
    blacklist_id = get_previous_followed('blacklist_ids.txt')
    if user_id in blacklist_id:
        status = True
    return status


def check_whitelist_id(user_id):
    status = False
    blacklist_id = get_previous_followed('whitelist_ids.txt')
    if user_id in blacklist_id:
        status = True
    return status


# Unfollow actions
def unfollow_actions(account_array,selection):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name = user.screen_name

    if int(selection) == 1:
        unfollow_non_follow_backs(account_array)
    elif int(selection) == 2:
        for account in accounts:
            api = set_twitter_auth(account)
            user = api.get_user(screen_name=account['USER_NAME'])
            screen_name = user.screen_name

            # Getting own Following and followers
            followers_ids = get_user_followers(api, screen_name)
            print('followers_ids@@@',followers_ids)
            for follower_id in followers_ids:
                state = dp_check(api.get_user(user_id=follower_id))
                if state == True:
                    unfollow_user(api, follower_id)
    elif int(selection) == 3:
        for account in accounts:
            api = set_twitter_auth(account)
            user = api.get_user(screen_name=account['USER_NAME'])
            screen_name = user.screen_name

            # Getting own Following and followers
            followers_ids = get_user_followers(api, screen_name)
            for follower_id in followers_ids:
                state = last_tweeted(api.get_user(user_id=follower_id))
                if state == False:
                    unfollow_user(api, follower_id)
    elif int(selection) == 4:
        for account in accounts:
            api = set_twitter_auth(account)
            user = api.get_user(screen_name=account['USER_NAME'])
            screen_name = user.screen_name

            # Getting own Following and followers
            followers_ids = get_user_followers(api, screen_name)
            for follower_id in followers_ids:
                state = dp_check(api.get_user(user_id=follower_id))
                if state == True:
                    unfollow_user(api, follower_id)
    else:
        print("No option selected")

#Follow users with a specific selection
# def follow_actions(accounts_array, selection):
#     # Authentication
#     for account in accounts_array:
#         api = set_twitter_auth(account)
#         user = api.get_user()
#         screen_name = user.screen_name
#
#     if selection == 1:
#         not_following_back()
#     elif selection == 2:
#         no_profile_image()
#     elif selection == 3:
#         inactive_user()
#     elif selection == 4:
#         print("Unfollowed fake users")
#     else:
#         print("No option selected")


def block_user(api,screen_name):
    try:
        api.create_block(screen_name=screen_name)
        enter_in_record(screen_name,'block_list.txt')
        print("Blocked: ", screen_name)
    except Exception as e:
        print(e)

# Follow profiles that are following a specific profile
def follow_following_of_someone(account_array, user_name_for_followers):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name = user.screen_name
        user_id = user.id

        # Getting own Following and followers
        followers_ids = get_user_followers(api, screen_name)
        following_ids = get_user_friends(api, screen_name)

        # Getting followers of desired user
        user_following_ids = get_user_friends(api, user_name_for_followers)
        count = 0
        for user_following_id in user_following_ids:

            if user_following_id not in following_ids:
                if check_blacklist(api.get_user(user_id=user_following_id)) | check_blacklist_id(user_id):
                    print(api.get_user(user_id=user_following_id), " is in blacklist. Cannot Follow")
                else:
                    user_follow(api, user_following_id)
                    count = count + 1
                    print("Followed: ", api.get_user(user_id=user_following_id).screen_name, " from account: ", screen_name)
        print("Followed ", count, "users from account: ", screen_name)

def follow_followers_of_following_of_someone(account_array, user_name_for_followers):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name = user.screen_name
        user_id = user.id

        # Getting own Following and followers
        followers_ids = get_user_followers(api, screen_name)
        following_ids = get_user_friends(api, screen_name)

        # Getting followers of desired user
        user_following_ids = get_user_friends(api, user_name_for_followers)
        count = 0
        for user_following_id in user_following_ids:
           level_2_follower_ids = get_user_followers(api, api.get_user(user_id=user_following_id).screen_name)
           for level_2_follower_id in level_2_follower_ids:
               if level_2_follower_id not in following_ids:
                   if check_blacklist(api.get_user(user_id=level_2_follower_id).screen_name) | check_blacklist_id(level_2_follower_id):
                       print(api.get_user(level_2_follower_id).scree_name, " is in blacklist. Cannot Follow")
                   else:
                       user_follow(api, level_2_follower_id)
                       count = count + 1
                       print("Followed: ", api.get_user(user_id=level_2_follower_id).screen_name, " from account: ", screen_name)
           print("Followed ", count, "users from account: ", screen_name)


def follow_following_of_following_of_someone(account_array, user_name_for_followers):
    # Authentication
    for account in account_array:
        api = set_twitter_auth(account)
        user = api.get_user(screen_name=account['USER_NAME'])
        screen_name = user.screen_name
        user_id = user.id

        # Getting own Following and followers
        followers_ids = get_user_followers(api, screen_name)
        following_ids = get_user_friends(api, screen_name)

        # Getting followers of desired user
        user_following_ids = get_user_friends(api, user_name_for_followers)
        count = 0
        for user_following_id in user_following_ids:
            level_2_following_ids = get_user_friends(api, api.get_user(user_id=user_following_id).screen_name)
            for level_2_following_id in level_2_following_ids:
                if level_2_following_id not in following_ids:
                    if check_blacklist(api.get_user(user_id=level_2_following_id).screen_name) | check_blacklist_id(level_2_following_id):
                        print(api.get_user(user_id=level_2_following_id).scree_name, " is in blacklist. Cannot Follow")
                    else:
                        user_follow(api, level_2_following_id)
                        count = count + 1
                        print("Followed: ", api.get_user(user_id=level_2_following_id).screen_name, " from account: ", screen_name)
            print("Followed ", count, "users from account: ", screen_name)


#################################################### AMMAR FILTERS END ###########################################################


if __name__ == "__main__":
        selection = menu()
        print(selection)
        try:
            process_selection(selection)
        except Exception as e:
            print(e)
