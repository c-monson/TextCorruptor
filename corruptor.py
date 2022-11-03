import random
import re

from nltk.tokenize import word_tokenize

class Corruptor:

    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename

        # Some knobs to tweak
        self.email_regex = r"^.*X-FileName:.*?\n\n(.*)$"
        #self.email_regex = r".*FileName:(.*)"

        self.fraction_of_time_to_swap_neighbors = 0.1
        self.fraction_of_words_to_randomly_delete = 0.1

        self.fraction_of_words_to_misspell = 0.1
        self.fraction_of_content_words_to_replace_with_synonyms = 0.1
        self.fraction_of_stopwords_to_remove = 0.1

    def corrupt_file(self):
        with open(self.input_filename, encoding='utf-8') as input_file, \
             open(self.output_filename, 'w', encoding='utf-8') as output_file:

            enron_reader = csv.reader(input_file)

            counter = 0
            first_line = True
            for row in enron_reader:
                counter += 1
                if counter > 10:
                    return

                # Skip first line of Enron .csv file, it contains headers
                if first_line:
                    first_line = False
                    continue

                email = self.extract_email(row)
                corrupted_email = self.corrupt_one_email(email)
                # output_file.write(row)
                # output_file.write(corrupted_line)
                # output_file.write('\n')

    # An Enron email has a bunch of email header stuff and other junk to strip out
    # And then this will also tokenize the email and return the tokenized list
    def extract_email(self, row):
        email = row[1]
        email_match = re.search(self.email_regex, email, flags=re.DOTALL)
        clean_email = email_match.group(1)

        tokenized_email = word_tokenize(clean_email)

        return tokenized_email

    def corrupt_one_email(self, email):
        corrupted_email = email
        corrupted_email = self.corrupt_by_swapping_with_neighbors(corrupted_email)
        #corrupted_email = self.corrupt_by_deleting_words(corrupted_email)

        return corrupted_email

    # NLTK is not yet working for me :-(
    # I'm going to assume that it is working and that word_tokenize() will return a list of strings (each being a word)
    def corrupt_by_swapping_with_neighbors(self, email):

        output_email = []
        index = -1
        while index < len(email) - 2:
            index += 1

            random_value = random.random()
            if random_value < self.fraction_of_time_to_swap_neighbors:
                output_email[index] = email[index+1]
                output_email[index+1] = email[index]
                index += 1
                continue

            output_email[index] = email[index]

        if index == len(email) - 2:
            output_email[-1] = email[-1]

        return email

    def corrupt_by_deleting_words(self, line):
        return line


###################################

corruptor = Corruptor("/Users/christianmonson/Professional/BrackenFern/A.I. Talks/Students/Krish (Mm m.)/Enron dataset/emails.csv",
                      "/Users/christianmonson/Professional/BrackenFern/A.I. Talks/Students/Krish (Mm m.)/Enron dataset/corrupted.txt")

corruptor.corrupt_file()
