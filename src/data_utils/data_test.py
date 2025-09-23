import pprint
from data_utils.data_loader import import_candidate_file

word_list = import_candidate_file("./tests/test.html")
pprint.pprint(word_list)