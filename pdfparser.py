#part 0: general imports
import os
import subprocess
import json

#part 0.1: attempt to install extensions for you
try:
    subprocess.run(['pip', 'install', 'pypdf2'])
except:
    print("failed to install pypdf2, manually install it")
try:
    subprocess.run(['pip', 'install', 'tika'])
except:
    print("failed to install tika, manually install it")
try:
    subprocess.run(['pip', 'install', 'gensim'])
except:
    print("failed to install gensim, manually install it")
try:
    subprocess.run(['pip', 'install', 'sklearn'])
except:
    print("failed to install sklearn, manually install it")
    
import PyPDF2 # pip install pypdf2
from tika import parser # pip install tika
import gensim.parsing.preprocessing as gensim_preprocessing #pip install gensim
from sklearn.feature_extraction.text import TfidfVectorizer #pip install sklearn
import json #pip install json

#part 1: all fns
def find_pdfs(folder_path: str):
    """
    Finds all PDF files in a directory and its subdirectories.

    Args:
        folder_path: The path to the directory to search.

    Returns:
        A list of full paths to all PDF files found.
    """
    pdf_files = []
    for root, directories, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".pdf") or filename.endswith(".PDF"):
                pdf_files.append(os.path.join(root, filename))
    return pdf_files


def extract_text_pdf2(pdf_path: str) -> str:
    """
    Given pdf's path, return the extracted version of the PDF

    Args:
        pdf_path: The directory

    Returns:
        The string of pdf converted into text
    """
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text


def extract_text_pdf(pdf_path: str):
    """
    Given pdf's path, return the extracted version of the PDF
    alternative way if the above does not work
    Args:
        pdf_path: The directory

    Returns:
        The string of pdf converted into text
    """
    from tika import parser # pip install tika
    raw = parser.from_file(pdf_path)
    return raw['content']


def save_string_to_file(text: str, filename: str ="output.txt"):
    """
    Saves a string to a text file in the current working directory.

    Args:
        text: The string to save.
        filename (optional): The desired filename (default: "output.txt").
    """
    with open(filename, "w", encoding="utf-8") as text_file:
        text_file.write(text)
    return None

def save_json_to_file(data: dict|list, filename: str ="output.json"):
    """
    This function writes a Python dictionary or list (JSON object) to a file.

    Args:
        data: The Python dictionary or list (JSON object) to be exported.
        filename: The name (including path) of the file to write the JSON data to.
    """
    try:
    # Open the file in write mode with UTF-8 encoding for proper JSON representation
        with open(filename, "w", encoding="utf-8") as f:
            # Use json.dump to serialize the data (convert to JSON string) and write it to the file
            json.dump(data, f, ensure_ascii=False)  # Ensure all characters are encoded correctly
            print(f"JSON data written to file: {filename}")

    except Exception as e:
        print(f"Error writing JSON data to file: {e}")


def initial_parse(text: str):
    """
    This function removes common words and prepositions from a string using Gensim.

    Args:
        text: The long string to be processed.

    Returns:
        A string with common words and prepositions removed.
    """
    
    # Add additional prepositions you want to remove (optional)
    words_to_remove = ["understand","professor","like","us","ii","iii","iv","vi","mhf","www","org"]

    # Tokenize the text (split into words)
    tokens = gensim_preprocessing.preprocess_string(
                gensim_preprocessing.remove_stopwords(
                    gensim_preprocessing.remove_stopwords(text.lower())
                    ,words_to_remove))

    return " ".join(tokens)


def run_tfidf(words):
    """
    This function calculates TF-IDF scores for a list of words.

    Args:
        words: words seperated by spacebars (strings) to be processed.

    Returns:
        A dictionary containing the TF-IDF scores for each word in the list.
    """
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit the vectorizer to the document (learn vocabulary and IDF)
    vectorizer.fit([words])

    # Transform the document into TF-IDF vectors
    # As we have a single document, this will result in a sparse matrix with a single row.
    tfidf_matrix = vectorizer.transform([words])

    # Extract word-TF-IDF score pairs as a dictionary
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))

    return tfidf_scores


# Example usage
pdf_filepath = os.path.join(os.getcwd(),"test")
#"./pdf-files"
final = ""
loop = find_pdfs(pdf_filepath)
for cnt,item in enumerate(loop):
    final += (_:=initial_parse(extract_text_pdf(item)))
    save_json_to_file(a:=run_tfidf(_),"tfidf" + str(cnt) + ".json")
    save_json_to_file({k: v for k, v in sorted(a.items(), key=lambda item: item[1])},"sortedtfidf" + str(cnt) + ".json")
    #final += initial_parse(extract_text_pdf2(x)) #this one is less clean
save_string_to_file(final,"textoutput.txt")

