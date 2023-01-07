
import csv
import json
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

csv.field_size_limit(10000000)

class Corruptor:

    CLEAN = 'clean'
    CORRUPT = 'corrupt'

    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename

        self.stopWords = set(stopwords.words('english'))

        # Some knobs to tweak
        self.email_regex = r"^.*X-FileName:.*?\n\n(.*)$"

        # Many emails have embedded forwarded email text inside them. The embeded text
        # has all kinds of fields (like "To:", the date, etc.) that are not useful for our natural
        # text decorruptor. So this regex matches the "Forward header" and strips it out. (Leaving
        # the actual text of the forwarded email itself).
        self.forwarded_regex = r"[^\n]*Forwarded by.*?Subject:[^\n]*"

        self.fraction_of_time_to_swap_neighbors = 0.03
        self.fraction_of_words_to_randomly_delete = 0.03

        #self.fraction_of_words_to_misspell = 0.1
        self.fraction_of_content_words_to_replace_with_synonyms = 0.15
        self.fraction_of_stopwords_to_remove = 0.03

    def corrupt_file(self):
        with open(self.input_filename, encoding='utf-8') as input_file, \
             open(self.output_filename, 'w', encoding='utf-8') as output_file:

            enron_reader = csv.reader(input_file)

            counter = 0
            first_line = True
            for row in enron_reader:
                counter += 1

                # Debugging
                #if counter % 15 == 0:
                #    break

                # Skip first line of Enron .csv file, it contains headers
                if first_line:
                    first_line = False
                    continue

                email = self.extract_email(row)
                corrupted_email = self.corrupt_one_email(email)

                one_email = {}

                one_email[Corruptor.CLEAN] = ' '.join(email)
                one_email[Corruptor.CORRUPT] = ' '.join(corrupted_email)

                if counter % 5000 == 0:
                    print(f"Sentence #: {counter}")
                    print(f"      email: {one_email[Corruptor.CLEAN]}")
                    print(f"  corrupted: {one_email[Corruptor.CORRUPT]}")
                    print()
                output_file.write(json.dumps(one_email))
                output_file.write('\n')

    # An Enron email has a bunch of email header stuff and other junk to strip out
    # And then this will also tokenize the email and return the tokenized list
    def extract_email(self, row):
        email = row[1]
        email_match = re.search(self.email_regex, email, flags=re.DOTALL)
        clean_email = email_match.group(1)

        clean_email_no_forward_text = re.sub(self.forwarded_regex, "", clean_email, flags=re.DOTALL)

        # Debugging
        #if clean_email is not clean_email_no_forward_text:
        #    print(f"CLEAN: ")
        #    print(clean_email)
        #    print("NO FORWARD")
        #    print(clean_email_no_forward_text)

        tokenized_email = nltk.word_tokenize(clean_email_no_forward_text)

        return tokenized_email

    def corrupt_one_email(self, email):
        corrupted_email = email
        corrupted_email = self.corrupt_by_swapping_with_neighbors(corrupted_email)
        corrupted_email = self.corrupt_by_deleting_words(corrupted_email)
        corrupted_email = self.corrupt_by_deleting_stop_words(corrupted_email)
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
            word_lower = word.lower()

            if word_lower in self.stopWords:
                output_email.append(word)
                continue

            random_value = random.random()
            if random_value > self.fraction_of_content_words_to_replace_with_synonyms:
                output_email.append(word)
                continue

            # Find all the synonyms (i.e. lemmas in any synsets of 'word') whose surface forms
            # are not identical to the word itself (a surprising number *are*!)
            #
            # If this word is not in WordNet or if all the synonyms are actually just the same word form
            # then we'll just skip this word.
            synonym_surface_forms = set()
            synsets = wordnet.synsets(word)
            for synset in synsets:
                synonym_lemmas = synset.lemmas()
                for synonym_lemma in synonym_lemmas:
                    synonym_surface_form = synonym_lemma.name()
                    if synonym_surface_form != word_lower:
                        synonym_surface_forms.add(synonym_surface_form)

            if len(synonym_surface_forms) == 0:
                output_email.append(word)
                continue

            # else: replace word
            synonym_surface_forms = list(synonym_surface_forms)

            # pick a random synset that word participates in
            random_synonym_surface_form_index = random.randrange(len(synonym_surface_forms))
            surface_form = synonym_surface_forms[random_synonym_surface_form_index]
            surface_form = surface_form.replace('_', ' ')
            output_email.append(surface_form)

        return output_email


###################################

random.seed(1) # For repeatability

corruptor = Corruptor("/Users/christianmonson/Professional/BrackenFern/A.I. Talks/Students/Krish (Mm m.)/Enron dataset/emails.csv",
                      "/Users/christianmonson/Professional/BrackenFern/A.I. Talks/Students/Krish (Mm m.)/Enron dataset/corrupted_noForwardText.json")

corruptor.corrupt_file()
