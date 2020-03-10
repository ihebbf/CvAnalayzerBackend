import io
import re
import pandas as pd
import spacy
import datetime

from project.utils.CVs import *
from project.utils import currentPath
from collections import Counter
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from spacy.matcher import Matcher

nlp = spacy.load('fr_core_news_md')
matcher = Matcher(nlp.vocab)


# function that extract all text from cv
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        # iterate over all pages of PDF document
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            # creating a resoure manager
            resource_manager = PDFResourceManager()
            # create a file handle
            fake_file_handle = io.StringIO()

            # creating a text converter object
            converter = TextConverter(
                resource_manager,
                fake_file_handle,
                laparams=LAParams()
            )
            # creating a page interpreter
            page_interpreter = PDFPageInterpreter(
                resource_manager,
                converter
            )
            # process current page
            page_interpreter.process_page(page)
            # extract text
            text = fake_file_handle.getvalue()
            yield text
            # close open handles
            converter.close()
            fake_file_handle.close()


# return common letters between two strings
def CountCommonChar(s1, s2):
    s3 = s1.lower()
    s4 = s2.lower()
    common_letters = Counter(s3) & Counter(s4)
    return sum(common_letters.values())


# function that extract mobile number from cv
def extract_mobile_number(text):
    pattern = re.compile(
        r'(\+\d{3}\s\d{8})|(\+\d{3}\s\d{2}.\d{3}.\d{3})|(\+\d{3}\s\d{2}\s\d{3}\s\d{3})|(\d{2}\s\d{3}\s\d{3})|(\d{2}.\d{3}.\d{3})|(\d{2}-\d{3}-\d{3})|(\(\+\d{3}\)\s\d{8})')
    phone = pattern.findall(text)
    if phone:
        number = ''.join(phone[0])
        return number


# function that extract email from cv
def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].lower()
        except IndexError:
            return None


# function that extract name from cv
def extract_name(resume_text):
    PersonsMatches = []
    ListSub = []
    Persons = []
    nlp_text = nlp(resume_text)

    pattern = [{'LIKE_EMAIL': False, 'LIKE_NUM': False, 'LIKE_URL': False, "IS_ALPHA": True},
               {'LIKE_EMAIL': False, 'LIKE_NUM': False, 'LIKE_URL': False, "IS_ALPHA": True},
               {'LIKE_EMAIL': False, 'LIKE_NUM': False, 'LIKE_URL': False, "IS_ALPHA": True, 'OP': '?'}]
    matcher.add('NAME', None, pattern)
    matches = matcher(nlp_text)
    if extract_email(resume_text) is None:
        return None
    else:
        for match in matches:
            PersonsMatches.append(nlp_text[match[1]:match[2]])

        for Person in PersonsMatches:
            nlp_person = nlp(Person.text)

            if (nlp_person[0].text.lower() in extract_email(resume_text).lower() and nlp_person[
                -1].text.lower() in extract_email(resume_text).lower()):
                Persons.append(Person.text)
                ListSub.append(CountCommonChar(Person.text, extract_email(resume_text)))
        print(Persons)
        if len(ListSub) == 0:
            return None
        else:
            maxMatch = max(ListSub)
            max_index = ListSub.index(maxMatch)
            return Persons[max_index]


# function that extract skills from cv
def extract_skills(resume_text):
    nlp_text = nlp(resume_text)
    noun_chunks = nlp_text.noun_chunks
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]

    # reading the csv file
    data = pd.read_csv(os.path.join(currentPath,'skills.csv'))

    # extract values
    skills = list(data.columns.values)
    skillset = []

    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams (example: machine learning)
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)

    return [i.capitalize().lower() for i in set([i.lower() for i in skillset])]


# function that extract languages from cv
def extract_langues(resume_text):
    nlp_text = nlp(resume_text)
    noun_chunks = nlp_text.noun_chunks
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    # reading the csv file
    data = pd.read_csv(os.path.join(currentPath,'langue.csv')).apply(lambda x: x.astype(str).str.lower())
    # extract values
    skills = list(data.columns.str.lower().values)
    skillset = []
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams (example: machine learning)
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)

    return [i.capitalize().lower() for i in set([i.lower() for i in skillset])]


# function that extract age from cv
def extract_age(text):
    match = re.findall(r'\d{4}', text)
    age = []
    for m in match:
        date = datetime.datetime.strptime(m, '%Y').strftime("%Y")

        if 1960 < int(date) < 2000:
            now = datetime.datetime.now()
            age.append((int(now.year) - int(date)))

    if len(age) == 0:
        return None
    else:
        return max(age)


# function that extract years of experience from cv
def extract_Year_of_experience(text):
    match = re.findall(r'\d{4}', text)
    experience = []
    print(experience)
    for m in match:
        date = datetime.datetime.strptime(m, '%Y').strftime("%Y")
        now = datetime.datetime.now()
        if extract_age(text) is not None:

            if ((int(now.year) - extract_age(text)) + 1) < int(date) < int(now.year):
                print(int(date), extract_age(text))
                experience.append(int(date))
        else:
            if 2000 < int(date) < int(now.year):
                experience.append(int(date))
    if len(experience) == 0:
        return None
    else:
        return max(experience) - min(experience)


# function that loop all cvs
def loopAllCv():
    text = ''
    resume_list = []
    CvNumber = len([name for name in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, name))]) - 1
    for i in range(CvNumber):

        filename = os.path.join(filepath, 'cv'+str(i + 1)+'.pdf')
        print(filename)
        for page in extract_text_from_pdf(filename):
            text += ' ' + page
        text = " ".join(text.split())
        resume_list.append(text)
        text = ''
    return resume_list

# function that return the frequency of each word in text
# def WordFrequency():
#     text = ''
#     for page in extract_text_from_pdf("CVs/c102.pdf"):
#         text += ' ' + page
#     stop = stopwords.words('english')
#     tokenized_word = word_tokenize(text)
#     liste = [i for i in tokenized_word if i not in stop]
#     words = [list.lower() for list in liste if list.isalpha()]
#     fdist = FreqDist(words)
#     fdist.plot(50, cumulative=False)
#     plt.show()
