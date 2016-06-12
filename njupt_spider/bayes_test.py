from bs4 import BeautifulSoup
def bayes_test(html_doc, p):
    soup = BeautifulSoup(html_doc, 'html.parser')
    ptagnum = len(soup.find_all('p'))
    if ptagnum >= 4:
        return True;
    else:
        return False;
