from urllib.request import urlopen

# def fetch_words():
#     story = urlopen('http://sixty-norty.com/c/t.txt')
def fetch_words(url):
    story = urlopen(url)
    story_words = []
    for line in story:
    ​    line_words = line.split()
    ​    for work in line_words:
    ​        sotry_words.append(work)
    story.close()
    return story_words

def print_items(items):
    for item in items:
        print(item)

# def main():
#     url = sys.args[0] #cannot put here
#     words = fetch_words()
#     print_items(items)

def main(url):
    words = fetch_words(url)
    print_items(items)


if __name__ == '__main__':
    main(sys.args[1])