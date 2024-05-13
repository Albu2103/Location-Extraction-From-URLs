import csv
import random

def select_random_links(input_file, output_file, num_links):
    with open(input_file, 'r', newline='') as f:
        reader = csv.reader(f)
        links = list(reader)

    # Select random links
    random_links = random.sample(links, num_links)

    # Add "https://" to each link
    for i, link in enumerate(random_links):
        random_links[i] = ['https://' + link[0]]
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(random_links)


input_file = 'List_of_companies.csv'  
output_file = 'random_100.csv'  
num_links = 100  

select_random_links(input_file, output_file, num_links)
