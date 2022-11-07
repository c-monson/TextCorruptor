
import csv
import random
import re

import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet

# Fixing the nltk error was easier than I thought. I just needed this magic line.
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')


class Corruptor:

    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename

        self.stopWords = set(stopwords.words('english'))

        # Some knobs to tweak
        self.email_regex = r"^.*X-FileName:.*?\n\n(.*)$"

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

                rejoined_email = ' '.join(email)
                rejoined_corrupted_email = ' '.join(corrupted_email)

                print(f"email:     {rejoined_email}")
                print(f"corrupted: {rejoined_corrupted_email}")
                output_file.write(rejoined_email + '\n')
                output_file.write(rejoined_corrupted_email + '\n')
                output_file.write('\n')

    # An Enron email has a bunch of email header stuff and other junk to strip out
    # And then this will also tokenize the email and return the tokenized list
    def extract_email(self, row):
        email = row[1]
        email_match = re.search(self.email_regex, email, flags=re.DOTALL)
        clean_email = email_match.group(1)

        tokenized_email = nltk.word_tokenize(clean_email)

        return tokenized_email

    def corrupt_one_email(self, email):
        corrupted_email = email
        #corrupted_email = self.corrupt_by_swapping_with_neighbors(corrupted_email)
        #corrupted_email = self.corrupt_by_deleting_words(corrupted_email)
        #corrupted_email = self.corrupt_by_deleting_stop_words(corrupted_email)
        corrupted_email = self.corrupt_by_replacing_with_synonym(corrupted_email)

        return corrupted_email

    def corrupt_by_swapping_with_neighbors(self, email):

        output_email = []
        index = -1
        while index < len(email) - 2:
            index += 1

            random_value = random.random()
            if random_value < self.fraction_of_time_to_swap_neighbors:
                output_email.append(email[index+1])
                output_email.append(email[index])
                index += 1
                continue

            output_email.append(email[index])

        # If we didn't swap the last 2 words (i.e. index will be len(email)-2 and not len(email)-1) then tack on the final word
        if index == len(email) - 2:
            output_email.append(email[-1])

        return output_email

    def corrupt_by_deleting_words(self, email):
        output_email = []
        for word in email:

            random_value = random.random()
            if random_value > self.fraction_of_words_to_randomly_delete:
                output_email.append(word)

        return output_email

    def corrupt_by_deleting_stop_words(self, email):

        output_email = []
        for word in email:
            skip_word = False
            if word in self.stopWords:
                random_value = random.random()
                if random_value < self.fraction_of_stopwords_to_remove:
                    skip_word = True

            if not skip_word:
                output_email.append(word)

        return output_email

    def corrupt_by_replacing_with_synonym(self, email):
        output_email = []
        for word in email:
            replace_word = False
            if word not in self.stopWords:
                random_value = random.random()
                if random_value < self.fraction_of_stopwords_to_remove:
                    replace_word = True

            # Check if this word is in WordNet
            if replace_word:
                synsets = wordnet.synsets(word)
                if len(synsets) == 0:
                    replace_word = False

            if not replace_word:
                output_email.append(word)
                continue


            # else: replace word

            # pick a random synset that word participates in
            random_synset_index = random.randrange(len(synsets))
            synset = synsets[random_synset_index]

            # Get the words (aka 'lemmas') in the synset
            synonym_lemmas = synset.lemmas()

            # Pick a random synonym (aka lemma) in the synset
            random_lemma_index = random.randrange(len(synonym_lemmas))
            synonym_lemma = synonym_lemmas[random_lemma_index]
            output_email.append(synonym_lemma.name())

        return output_email


###################################

random.seed(1) # For repeatability

corruptor = Corruptor("/Users/christianmonson/Professional/BrackenFern/A.I. Talks/Students/Krish (Mm m.)/Enron dataset/emails.csv",
                      "/Users/christianmonson/Professional/BrackenFern/A.I. Talks/Students/Krish (Mm m.)/Enron dataset/corrupted.txt")

corruptor.corrupt_file()
