from Bio import Entrez
import csv
import time
from datetime import datetime, timedelta
from calendar import monthrange


email_id = ''
def search_pubmed(author_id, email_id):
    print(email_id)
    Entrez.email = email_id
    
    handle = Entrez.esearch(db="pubmed", term=author_id, retmax=50000, reldate=48*30)
    record = Entrez.read(handle)
    idlist = record["IdList"]
    output = []
    for pmid in idlist:
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="medline", retmode="text")
        record = handle.read()
        handle.close()

        # Parse the MEDLINE record and extract the information
        org_affiliation_str = ''

        pub_date_str = ''
        pub_date_fin = ''
        line_auth_id = ''
        collaborator = ''
        author_match = False
        for line in record.split('\n'):
            if line.startswith('FAU - '):
                collaborator = line[6:]
            elif line.startswith('AUID-'):
                line_auth_id = line[13:]

                if line_auth_id == author_id:
                    author_match = True                
            elif line.startswith('AD  - ') and org_affiliation_str == '' and collaborator:
                org_affiliation_str = line[5:]
            elif line.startswith('DP  - '):
                pub_date_str = line[6:]
                if pub_date_str:
                # Convert date string to datetime object
                    try:
                        pub_date = datetime.strptime(pub_date_str, '%Y %b %d')
                    except ValueError:
                        pub_date = datetime.strptime(pub_date_str, '%Y %b')

                    year = pub_date.strftime('%y')
                    month = pub_date.strftime('%#m')
                    day = pub_date.strftime('%#d')
                    if day == '00':
                        day = str(monthrange(int(pub_date.strftime('%Y')), int(month))[1])
                    pub_date_fin = f'{month}/{day}/{year}'

            if author_match == True:
                collaborator = ''
                line_auth_id = ''
                author_match = False
                org_affiliation_str = ''
                 # Append a row for each collaborator


            if collaborator and org_affiliation_str and pub_date_fin:
                output.append([collaborator, org_affiliation_str, pub_date_fin])
                pub_date_str = ''
                #pub_date_fin = ''
                line_auth_id = ''
                collaborator = ''
                org_affiliation_str = ''
    # Write output to CSV
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Collaborators', 'Organizational Affiliation', 'Publication Date'])
        writer.writerows(output)

    return output

if __name__ == '__main__':
    author_id = input('Please enter ORCID in the format XXXX-XXXX-XXXX-XXXX:\n')
    email_id = input('Please enter your email for use with pubmed API:\n')
    search_pubmed(author_id, email_id)