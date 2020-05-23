import json
import pandas as pd
import urllib
import time

MOBILE  = 'mobile'
DESKTOP = 'desktop'

# You should set absolute url if using this script via crontab
SCRIPT_URL = "./"
# Filename of csv file with urls you would like to scan (
#       scheme: column name: url, 
#       1 row is header wiht column names)
URLS_CSV   = "file-with-urls.csv"

# get your api key here https://developers.google.com/speed/docs/insights/v5/get-started
API_KEY = 'your-google-psi-api-key'

def new_parse_dataframe():
    return pd.DataFrame(
    columns=['url',
        'FCP_category',
        'FCP_percentile',
        'FID_category',
        'FID_percentile',
        'Time_to_Interactive',
        'Speed_Index',
        'First_CPU_Idle',
        'First_Meaningful_Paint',
        'TTFB',
        'Total_Blocking_Time'])  

def get_psi_response(url_list, strategy_type):

    response_object = {}

    for i in range(0, len(url_list)):

        # Get testing url
        url = testing_urls.iloc[i][testing_urls_column_header]
        print("{} - Parsing url is {}".format(strategy_type, url))
        # Make request
        pagespeed_results = urllib.urlopen('https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={}&strategy={}&key={}'\
            .format(url, strategy_type, API_KEY)).read().decode('UTF-8')
        # Convert to json format
        pagespeed_results_json = json.loads(pagespeed_results)
        # Insert returned json response into response_object
        response_object[url] = pagespeed_results_json
        time.sleep(1)
    
    return response_object

def run_testing(url_list, strategy_type):

    pagespeed_results_data = new_parse_dataframe()
    response_object       = get_psi_response(url_list, strategy_type)

    for (url, i) in zip(
    response_object.keys(),
    range(0, len(response_object))):

        # URLs
        pagespeed_results_data.loc[i, 'url'] =\
            response_object[url]['lighthouseResult']['finalUrl']

        # First Contentful Paint 
        fcp = response_object[url]\
            ['loadingExperience']['metrics']['FIRST_CONTENTFUL_PAINT_MS']

        # First Input Delay 
        fid = response_object[url]\
            ['loadingExperience']['metrics']['FIRST_INPUT_DELAY_MS']

        # First Contentful Paint Metrics     
        pagespeed_results_data.loc[i, 'FCP_category'] = fcp['category']
        pagespeed_results_data.loc[i, 'FCP_percentile'] = fcp['percentile']

        # First Input Delay Metrics     
        pagespeed_results_data.loc[i, 'FID_category'] = fid['category']
        pagespeed_results_data.loc[i, 'FID_percentile'] = fid['percentile']

        # Time to Interactive  
        pagespeed_results_data.loc[i, 'Time_to_Interactive'] =\
        response_object[url]['lighthouseResult']['audits']['interactive']['displayValue']

        # Speed Index
        pagespeed_results_data.loc[i, 'Speed_Index'] =\
        response_object[url]['lighthouseResult']['audits']['speed-index']['displayValue']

        # First CPU Idle
        pagespeed_results_data.loc[i, 'First_CPU_Idle'] =\
        response_object[url]['lighthouseResult']['audits']['first-cpu-idle']['displayValue']

        # First Meaningful Paint    
        pagespeed_results_data.loc[i, 'First_Meaningful_Paint'] =\
        response_object[url]['lighthouseResult']['audits']['first-meaningful-paint']['displayValue']

        # Time to First Byte    
        pagespeed_results_data.loc[i, 'TTFB'] =\
        response_object[url]['lighthouseResult']['audits']['time-to-first-byte']['displayValue']

        # Total Blocking Time   
        pagespeed_results_data.loc[i, 'Total_Blocking_Time'] =\
        response_object[url]['lighthouseResult']['audits']['total-blocking-time']['displayValue']

    save_result_to_csv(pagespeed_results_data, strategy_type)

def save_result_to_csv(summary, strategy_type):
    # Create dataframe to store field data responses
    current_datetime = time.strftime("%Y-%b-%d-%H%M%S")
    export_filename  = '{}psi-results-{}-{}.csv'.format(SCRIPT_URL, strategy_type, current_datetime)
    summary.to_csv(export_filename, sep=';', index = False, encoding='utf-8', quotechar='"')

# Read Testing Urls
testing_urls_column_header = 'url'
testing_urls = pd.read_csv('{}{}'.format(SCRIPT_URL, URLS_CSV), header=None, names=[testing_urls_column_header])

run_testing(testing_urls, MOBILE)
run_testing(testing_urls, DESKTOP)
