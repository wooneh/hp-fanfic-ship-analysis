import requests, json, time, re
from bs4 import BeautifulSoup
from chord import Chord
import copy

# Scraper thanks to Allison King
# https://github.com/allisonking/fanfic-analysis

def get_genres(genre_text):
    if genre_text.startswith('Chapters'):
        return []
    genres = genre_text.split('/')
    # Hurt/Comfort is annoying because of the '/'
    corrected_genres = []
    for genre in genres:
        if genre == 'Hurt':
            corrected_genres.append('Hurt/Comfort')
        elif genre == 'Comfort':
            continue
        else:
            corrected_genres.append(genre)
    return corrected_genres


def scrape_all_stories_on_page(url, metadata_list):
    # names of the classes on fanfiction.net
    story_root_class = 'z-list zhover zpointer'

    html = requests.get(url).content
    soup = BeautifulSoup(html, "html.parser")

    # get all the stories on the page
    all_stories_on_page = soup.find_all('div', class_=story_root_class)

    for story in all_stories_on_page:
        story_id, metadata = scrape_story_blurb(story)
        metadata_list[story_id] = metadata
    return metadata_list


def scrape_story_blurb(story):
    # names of the classes on fanfiction.net
    title_class = 'stitle'
    metadata_div_class = 'z-padtop2 xgray'
    backup_metadata_div_class = 'z-indent z-padtop'

    # title = story.find(class_=title_class).get_text()
    story_id = story.find(class_=title_class)['href'].split("/")[2]

    metadata_div = story.find('div', class_=metadata_div_class)

    # this happened once, on story ID 268931
    if metadata_div is None:
        metadata_div = story.find('div', class_=backup_metadata_div_class)
        start_idx = metadata_div.text.index('Rated')
        metadata_div_text = metadata_div.text[start_idx:]
    else:
        metadata_div_text = metadata_div.get_text()

    metadata_parts = metadata_div_text.split('-')
    metadata = {}

    # see if we have characters and/or completion
    last_part = metadata_parts[len(metadata_parts) - 1].strip()
    if last_part == 'Complete':
        # metadata['status'] = 'Complete'
        # have to get the second to last now
        second_to_last = metadata_parts[len(metadata_parts) - 2].strip()
        if second_to_last.startswith('Published'):
            metadata['characters'] = []
        else:
            metadata['characters'] = get_characters_from_string(second_to_last)
    else:
        # metadata['status'] = 'Incomplete'
        if last_part.startswith('Published'):
            metadata['characters'] = []
        else:
            metadata['characters'] = get_characters_from_string(last_part)

    return story_id, metadata


def get_characters_from_string(string):
    stripped = string.strip()
    if stripped.find('[') == -1:
        return stripped.split(', ')
    else:
        characters = []
        num_pairings = stripped.count('[')
        for idx in range(0, num_pairings):
            open_bracket = stripped.find('[')
            close_bracket = stripped.find(']')
            pairing = get_characters_from_string(stripped[open_bracket + 1 :close_bracket])
            characters.append(pairing)
            stripped = stripped[close_bracket+1:]
        if stripped != '':
            singles = get_characters_from_string(stripped)
            [characters.append(character) for character in singles]
        return characters


def main():
    # we're only going to look at harry potter fanfics
    base_url = "https://www.fanfiction.net/book/Harry-Potter"
    # this gets appended in order to
    page_suffix = "?&srt=1&lan=1&g1=2&r=10&p="

    # 2 seconds seems reasonable for a human to quickly scroll through a page
    rate_limit = 2

    metadata_list = {}
    first_page = 1
    last_page = 13129
    pages = range(last_page, first_page - 1, -1)
    for page in pages:
        # log
        print("Scraping page {0}".format(page))

        # build the url
        url = '{0}/{1}{2}'.format(base_url, page_suffix, str(page))

        # and let's go!
        metadata_list = scrape_all_stories_on_page(url, metadata_list)

        # sleep to be good about terms of service
        time.sleep(rate_limit)

    filename = 'data.json'
    with open(filename, 'w') as outfile:
        json.dump(metadata_list, outfile)


if __name__ == "__main__":
    main()
