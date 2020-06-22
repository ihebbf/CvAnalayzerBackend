import io
import re
import pandas as pd
import spacy
import datetime
import string

from project.utils.CVs import *

from project.utils.Keywords import keywordpath
from collections import Counter
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from spacy.matcher import Matcher

from project.utils.CvTmp import upload

nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)


# function that extract all text from CvTmp
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


# function that extract mobile number from CvTmp
def extract_mobile_number(text):
    pattern = re.compile(
        r'(\+\d{3}\s\d{8})|(\+\d{3}\s\d{2}.\d{3}.\d{3})|(\+\d{3}\s\d{2}\s\d{3}\s\d{3})|(\d{2}\s\d{3}\s\d{3})|(\d{2}.\d{3}.\d{3})|(\d{2}-\d{3}-\d{3})|(\(\+\d{3}\)\s\d{8})')
    phone = pattern.findall(text)
    if phone:
        number = ''.join(phone[0])
        return number


# function that extract email from CvTmp
def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].lower()
        except IndexError:
            return None


# function that extract name from CvTmp
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
        return "Non trouvé"
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
            return "Non trouvé"
        else:
            maxMatch = max(ListSub)
            max_index = ListSub.index(maxMatch)
            return Persons[max_index]


# function that extract skills from CvTmp
def extract_skills(resume_text):
    nlp_text = nlp(resume_text)
    noun_chunks = nlp_text.noun_chunks
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]

    # reading the csv file
    data = pd.read_csv(os.path.join(keywordpath,'skills.csv'))

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


# function that extract languages from CvTmp
def extract_langues(resume_text):
    nlp_text = nlp(resume_text)
    noun_chunks = nlp_text.noun_chunks
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    # reading the csv file
    data = pd.read_csv(os.path.join(keywordpath,'langue.csv')).apply(lambda x: x.astype(str).str.lower())
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



# function that extract age from CvTmp
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


# function that extract years of experience from CvTmp
def extract_Year_of_experience(text):
    match = re.findall(r'\d{4}', text)
    experience = []
    for m in match:
        date = datetime.datetime.strptime(m, '%Y').strftime("%Y")
        now = datetime.datetime.now()
        if extract_age(text) is not None:

            if ((int(now.year) - extract_age(text)) + 1) < int(date) < int(now.year):
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
    print(CvNumber)
    for i in range(CvNumber):

        filename = os.path.join(filepath, 'CvTmp'+str(i + 1)+'.pdf')
        print(filename)
        for page in extract_text_from_pdf(filename):
            text += ' ' + page
        text = " ".join(text.split())
        resume_list.append(text)
        text = ''
    return resume_list




# function that extract languages from CvTmp et tranforme la variable langue avec l'encodage binaire
def convert_langues_to_binary(resume_text):
    nlp_text = nlp(resume_text)
    noun_chunks = nlp_text.noun_chunks
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    # reading the csv file
    data = pd.read_csv(os.path.join(keywordpath,'langue.csv')).apply(lambda x: x.astype(str).str.lower())
    # extract values
    skills = list(data.columns.str.lower().values)
    skillset = []
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token.lower())


    # check for bi-grams and tri-grams (example: machine learning)
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token.lower())
    count=""
    for s in skills:
        if s in skillset:
            count+="1"
        else:
            count+="0"
    return int(count)



# function that extract languages from CvTmp et tranforme la variable langue avec l'encodage binaire
def convert_web_skills_to_binary(resume_text):
    nlp_text = nlp(resume_text)
    noun_chunks = nlp_text.noun_chunks
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    # reading the csv file
    data = pd.read_csv(os.path.join(keywordpath,'web.csv')).apply(lambda x: x.astype(str).str.lower())
    # extract values
    skills = list(data.columns.str.lower().values)

    skillset = []
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token.lower())


    # check for bi-grams and tri-grams (example: machine learning)
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token.lower())
    count=""
    skillset = list(dict.fromkeys(skillset))
    print(skillset)
    for s in skills:
        if skillset.count(s) > 0 :
            count+="1"
        else:
            count+="0"
    return count

def WordsFrequecy():
    text = "iheb Services zeinbe lé python nlp python -conception conception Services "
    doc = nlp(text)
    #remove stopwords and punctuations
    words = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    for i in range(len(words)):
        words[i]=words[i].strip(string.punctuation)

    word_freq = Counter(words)
    common_words = word_freq.most_common()




def loopOneOrAllCV(files):
    text = ''
    resume_list = []
    for f in files :
        filename = os.path.join(upload,f.filename)
        print(filename)
        for page in extract_text_from_pdf(filename):
            text += ' ' + page
        text = " ".join(text.split())
        resume_list.append(text)
        text = ''
    return resume_list