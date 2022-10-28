from nltk.tokenize import word_tokenize

class Corruptor:

    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename

        # Some knobs to tweak
        self.fraction_of_time_to_swap_neighbors = 0.1
        self.fraction_of_words_to_randomly_delete = 0.1

        self.fraction_of_words_to_misspell = 0.1
        self.fraction_of_content_words_to_replace_with_synonyms = 0.1
        self.fraction_of_stopwords_to_remove = 0.1

    def corrupt_file(self):
        with open(self.input_filename, encoding='utf-8') as input_file, \
             open(self.output_filename, 'w', encodings='utf-8') as output_file:

            first_line = True
            for line in input_file:

                # Skip first line of Enron .csv file, it contains headers
                if first_line:
                    first_line = False
                    continue

                email = self.extract_email(line)
                corrupted_line = self.corrupt_one_line(line)
                output_file.write(line)
                output_file.write(corrupted_line)
                output_file.write('\n')

    def corrupt_one_line(self, line):
        corrupted_line = line
        corrupted_line = self.corrupt_by_swapping_with_neighbors(corrupted_line)
        corrupted_line = self.corrupt_by_deleting_words(corrupted_line)

        return corrupted_line

    def corrupt_by_swapping_with_neighbors(self, line):


        return line

    def corrupt_by_deleting_words(self, line):


        return line

