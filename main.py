import time
from selenium import webdriver
from urllib.parse import urlparse, unquote
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pprint import pprint
import json
import os
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import re


def start(url, debug: bool = False):
    global driver

    if debug:
        print("[START] Initializing Chrome WebDriver...")

    driver = webdriver.Chrome()

    if debug:
        print(f"[START] Navigating to: {url}")

    driver.get(url)

    if debug:
        print(f"[START] Webpage loaded: {driver.current_url}")
        print("[START] WebDriver initialization complete.")
        print("-------------------------------------------------------")


def end(debug: bool = False):
    """
    Function to quit the WebDriver, closing the browser window.
    """
    global driver

    if debug:
        print("[END] Attempting to close the WebDriver...")

    if driver:
        driver.quit()

        if debug:
            print("[END] WebDriver closed successfully.")
    elif debug:
        print("[END] No active WebDriver was found.")


# this is only done so that I can print multiple error messages,
# since there's the same NoSuchElementException for each every element not found error
def find_required_element_helper(parent, by, selector, error_message):
    try:
        return parent.find_element(by, selector)
    except NoSuchElementException:
        raise NoSuchElementException(error_message) from None


# same logic as find_required_element_helper, just for multiple elements,
# uses find_elements instead of find_element
def find_required_elements_helper(parent, by, selector, error_message):
    try:
        return parent.find_elements(by, selector)
    except NoSuchElementException:
        raise NoSuchElementException(error_message) from None



def searchDojos(debug: bool):
    if debug:
        print("[searchDojos] Starting Dojo extraction...")

    pwnTree = {}

    if debug:
        print("[searchDojos] Searching for elements matching 'ul.card-list'...")

    ul_elements = find_required_elements_helper(
        driver,
        By.CSS_SELECTOR,
        "ul.card-list",
        """The ul elements inside the webpage doesn't exist.
        First check if the webpage is correct,
        then inspect the website and see if the dojos are inside a ul tag, or other tags,
        and change the parameter accordingly.
        -----------------------------------------------------------------"""
    )

    if debug:
        print(f"[searchDojos] Found {len(ul_elements)} ul.card-list element(s).")

        if not ul_elements:
            print("[searchDojos] WARNING: No Dojo card lists were found.")

    for ul_index, each_ul_element in enumerate(ul_elements, start=1):

        if debug:
            print(f"\n[searchDojos] Processing card list {ul_index}/{len(ul_elements)}...")

        a_elements = find_required_elements_helper(
            each_ul_element,
            By.TAG_NAME,
            "a",
            """The anchor tags inside the ul elements don't exist.
            Check the webpage and inspect the website to see
            whether the links are still inside anchor tags.
            ---------------------------------------------------------------"""
        )

        if debug:
            print(f"[searchDojos] Found {len(a_elements)} anchor tag(s) in this card list.")

            if not a_elements:
                print("[searchDojos] WARNING: This card list contains no anchor tags.")

        for a_index, each_a_element in enumerate(a_elements, start=1):

            if debug:
                print(
                    f"\n[searchDojos] Processing anchor "
                    f"{a_index}/{len(a_elements)}..."
                )

            href = each_a_element.get_attribute("href")

            if debug:
                print(f"[searchDojos] Extracted href: {href!r}")

            # Skip elements that do not have a URL
            if not href:
                if debug:
                    print("[searchDojos] Skipping anchor because it has no URL.")
                continue

            try:
                if debug:
                    print("[searchDojos] Searching for the element with class 'card-title'...")

                card_title_element = each_a_element.find_element(
                    By.CLASS_NAME,
                    "card-title"
                )

                dojoTitle = card_title_element.text.strip()

                if debug:
                    print(f"[searchDojos] Extracted Dojo title: {dojoTitle!r}")

                # Use the URL's last path segment if the title is empty
                if not dojoTitle:
                    if debug:
                        print("[searchDojos] WARNING: The card title is empty.")
                    raise NoSuchElementException("The card title is empty.")

            except NoSuchElementException:
                if debug:
                    print(f"[searchDojos] WARNING: No usable title found for href: {href}")

                print(f"There is no title for href: {href}")
                print("Using the last path segment of the URL as the title.")

                path_segments = [
                    segment
                    for segment in urlparse(href).path.split("/")
                    if segment
                ]

                dojoTitle = (
                    unquote(path_segments[-1])
                    if path_segments
                    else href
                )

                if debug:
                    print(f"[searchDojos] Fallback Dojo title: {dojoTitle!r}")

                print("Do manual entry of this href if you want to.")
                print("-------------------------------------------------------")

            # Add an index suffix only if the Dojo title already exists
            dojoKey = dojoTitle
            suffix = 1

            while dojoKey in pwnTree:
                if debug:
                    print(f"[searchDojos] Duplicate Dojo title found: {dojoKey!r}")
                    print(f"[searchDojos] Trying suffix _index{suffix}...")
                dojoKey = f"{dojoTitle}_index{suffix}"
                suffix += 1

            if debug:
                print(f"[searchDojos] Assigning dojo title: {dojoKey!r}")

            pwnTree[dojoKey] = {
                "dojoIndex": len(pwnTree) + 1,
                "href": href,
                "modules": {}
            }

            if debug:
                print(f"[searchDojos] Added Dojo: {dojoKey!r}")
                print(f"[searchDojos] Dojo URL: {href}")
                print(f"[searchDojos] Current number of Dojos: {len(pwnTree)}")

    if debug:
        print("\n[searchDojos] Dojo extraction complete.")
        print(f"[searchDojos] Total Dojos extracted: {len(pwnTree)}")
        print("-------------------------------------------------------")

    return pwnTree




def parseModules(pwnTree: dict[str, dict], debug: bool):
    if debug:
        print("[parseModules] Starting module extraction...")
        print(f"[parseModules] Total Dojos to process: {len(pwnTree)}")

    for dojo_index, (key, value) in enumerate(pwnTree.items(), start=1):
        module_counter = 1

        if debug:
            print(
                f"\n[parseModules] Processing Dojo "
                f"{dojo_index}/{len(pwnTree)}: {key!r}"
            )
            print(f"[parseModules] Dojo URL: {value['href']}")

        if debug:
            print("[parseModules] Navigating to the Dojo webpage...")

        driver.get(value["href"])

        if debug:
            print(f"[parseModules] Webpage loaded: {driver.current_url}")
            print("[parseModules] Searching for the module list ('ul.card-list')...")

        ul_element_modules = find_required_element_helper(
            driver,
            By.CSS_SELECTOR,
            "ul.card-list",
            (
                "The ul element having class 'card-list' doesn't exist inside the webpage. "
                "First check if the link is correct, "
                "then check if the first ul element having class 'card-list' "
                "is actually the ul with modules inside it or not. "
                "-------------------------------------------------------------------"
            )
        )

        if debug:
            print("[parseModules] Module list found.")
            print("[parseModules] Searching for anchor tags inside the module list...")

        a_elements = find_required_elements_helper(
            ul_element_modules,
            By.TAG_NAME,
            "a",
            """The anchor tags inside the ul elements don't exist.
            Check the webpage and inspect the website to see
            whether the links are still inside anchor tags.
            ---------------------------------------------------------------"""
        )

        if debug:
            print(f"[parseModules] Found {len(a_elements)} module anchor tag(s).")

            if not a_elements:
                print("[parseModules] WARNING: No module anchor tags were found.")

        # same code as the one above in searchDojos function
        for a_index, each_a_element in enumerate(a_elements, start=1):

            if debug:
                print(
                    f"\n[parseModules] Processing module anchor "
                    f"{a_index}/{len(a_elements)}..."
                )

            href = each_a_element.get_attribute("href")

            if debug:
                print(f"[parseModules] Extracted href: {href!r}")

            # Skip elements that do not have a URL
            if not href:
                if debug:
                    print("[parseModules] Skipping anchor because it has no URL.")
                continue

            try:
                if debug:
                    print("[parseModules] Searching for the element with class 'card-title'...")

                card_title_element = each_a_element.find_element(
                    By.CLASS_NAME,
                    "card-title"
                )

                moduleTitle = card_title_element.text.strip()

                if debug:
                    print(f"[parseModules] Extracted module title: {moduleTitle!r}")

                # Use the URL's last path segment if the title is empty
                if not moduleTitle:
                    if debug:
                        print("[parseModules] WARNING: The card title is empty.")
                    raise NoSuchElementException("The card title is empty.")

            except NoSuchElementException:
                if debug:
                    print(f"[parseModules] WARNING: No usable title found for href: {href}")

                print(f"There is no title for href: {href}")
                print("Using the last path segment of the URL as the title.")

                path_segments = [
                    segment
                    for segment in urlparse(href).path.split("/")
                    if segment
                ]

                moduleTitle = (
                    unquote(path_segments[-1])
                    if path_segments
                    else href
                )

                if debug:
                    print(f"[parseModules] Fallback module title: {moduleTitle!r}")

                print("Do manual entry of this href if you want to.")
                print("-------------------------------------------------------")

            # Add an index suffix only if the module title already exists
            # Same code as dojoTitle portion
            moduleKey = moduleTitle
            suffix = 1

            while moduleKey in value["modules"]:
                if debug:
                    print(f"[searchDojos] Duplicate Module title found: {moduleKey!r}")
                    print(f"[searchDojos] Trying suffix _index{suffix}...")
                moduleKey = f"{moduleTitle}_index{suffix}"
                suffix += 1

            if debug:
                print(f"[searchDojos] Assigning module title: {moduleKey!r}")

            value["modules"][moduleKey] = {
                "moduleIndex": f"{value['dojoIndex']}.{module_counter}",
                "href": href,
                "contents": {}
            }

            module_counter += 1

            if debug:
                print(f"[parseModules] Added module: {moduleKey!r}")
                print(f"[parseModules] Module URL: {href}")
                print(
                    f"[parseModules] Modules currently stored for "
                    f"{key!r}: {len(value['modules'])}"
                )

    return pwnTree


# the | None = None basically says its either a set or None
# we can also use indicesToParse = None directly, but we'd lost the type hint that its a set
# also can't do indicesToParse: set[str] = None since, None is not a set

def validParsingIndices(pwnTree: dict[str, dict], debug: bool = True, indicesToParse: set[str] | None = None
) -> list[str]:

    if debug:
        print("[validParsingIndices] Building list of valid indices...")

    validIndices = []

    for dojoData in pwnTree.values():
        validIndices.append(str(dojoData["dojoIndex"]))

        for moduleData in dojoData["modules"].values():
            validIndices.append(str(moduleData["moduleIndex"]))

    if debug:
        print(f"[validParsingIndices] Found {len(validIndices)} valid indices.")

    validParsingIndices = []



    if indicesToParse is not None:
        if debug:
            print(f"[validParsingIndices] Requested indices: {indicesToParse}")

        validIndicesLength = len(validIndices)

        for parsingIndex in indicesToParse:
            if "." not in parsingIndex:

                if parsingIndex not in validIndices:
                    if debug:
                        print(f"[validParsingIndices] Invalid Dojo index: {parsingIndex}")
                    continue

                if debug:
                    print(f"[validParsingIndices] Expanding Dojo {parsingIndex}...")

                positionOfDojoIndex = validIndices.index(parsingIndex)

                for i in range(positionOfDojoIndex + 1, validIndicesLength):
                    if not validIndices[i].startswith(parsingIndex + "."):
                        break

                    validParsingIndices.append(validIndices[i])

            else:
                if parsingIndex in validIndices:
                    validParsingIndices.append(parsingIndex)

                    if debug:
                        print(f"[validParsingIndices] Accepted module index: {parsingIndex}")

                elif debug:
                    print(f"[validParsingIndices] Invalid module index: {parsingIndex}")

    else:
        validParsingIndices = [
            index for index in validIndices
            if "." in index
        ]

        if debug:
            print("[validParsingIndices] No selection specified; selecting all modules.")

    # Removing duplicates while preserving order
    validParsingIndices = list(dict.fromkeys(validParsingIndices))

    if debug:
        print(f"[validParsingIndices] Selected {len(validParsingIndices)} modules.")

    return validParsingIndices



def buildModuleLookup(
    pwnTree: dict[str, dict],
    debug: bool = True,
    checkInTerminal: bool = False
) -> dict[str, dict]:

    if debug:
        print("[buildModuleLookup] Building module index-to-module lookup...")

    moduleLookup = {}

    for dojoData in pwnTree.values():
        for moduleData in dojoData["modules"].values():
            moduleIndex = str(moduleData["moduleIndex"])

            moduleLookup[moduleIndex] = moduleData

    if debug:
        print(f"[buildModuleLookup] Lookup contains {len(moduleLookup)} modules.")

    if checkInTerminal:
        pprint(moduleLookup)

    return moduleLookup


def parseContent(href: str, moduleData: dict, debug: bool = True):
    all_content = []

    if debug:
        print("[parseContent] Fetching module page...")
        print(f"[parseContent] URL: {href}")

    response = requests.get(href)
    response.raise_for_status()

    if debug:
        print(f"[parseContent] Page fetched: {response.url}")
        print("[parseContent] Parsing page HTML...")

    soup = BeautifulSoup(response.text, "html.parser")

    if debug:
        print("[parseContent] Searching for the accordion container...")

    challenge_div = soup.find("div", class_="accordion")

    if challenge_div is None:
        if debug:
            print("[parseContent] No accordion found. This page has no challenges.")
            print("[parseContent] Skipping this page.")

        moduleData["contents"]["content"] = ""
        return

    challenge_elements = challenge_div.find_all(
        "div",
        class_="accordion-item"
    )

    if debug:
        print(f"[parseContent] Found {len(challenge_elements)} challenge elements.")

    for i, challenge in enumerate(challenge_elements, start=1):
        if debug:
            print(f"[parseContent] Processing challenge {i}...")

        challenge_header_element = challenge.find(
            "div",
            class_="accordion-item-header"
        )

        if challenge_header_element is None:
            if debug:
                print(f"[parseContent] Challenge {i} has no header. Skipping.")
            continue

        title_span_element = challenge_header_element.find("span")

        if title_span_element is None:
            if debug:
                print(f"[parseContent] Challenge {i} has no title span. Skipping.")
            continue

        challenge_title = title_span_element.get_text(strip=True)

        challenge_body_element = challenge.find(
            "div",
            class_="accordion-item-body"
        )

        if challenge_body_element is None:
            if debug:
                print(f"[parseContent] Challenge {i} has no body. Skipping.")
            continue

        content_parts = []

        for element in challenge_body_element.find_all(
            ["p", "pre", "h1", "h2", "h3", "h4", "h5", "h6", "li"]
        ):
            if element.name == "pre":
                text = element.get_text()
            else:
                text = element.get_text(strip=True)

            if text.strip():
                content_parts.append(text)

                if debug:
                    print(
                        f"[parseContent] Extracted <{element.name}> "
                        f"({len(text)} characters)."
                    )

        if debug:
            print(
                f"[parseContent] Searching for iframes in challenge {i}..."
            )

        for iframe in challenge_body_element.find_all("iframe"):
            iframe_src = iframe.get("data-src")

            if iframe_src:
                parsed_url = urlparse(str(iframe_src))

                if parsed_url.hostname in {"www.youtube.com", "youtube.com"}:
                    if parsed_url.path.startswith("/embed/"):
                        video_id = parsed_url.path.split("/")[-1]
                        iframe_src = (
                            f"https://www.youtube.com/watch?v={video_id}"
                        )

                content_parts.append(iframe_src)

                if debug:
                    print(
                        f"[parseContent] Extracted iframe URL: {iframe_src}"
                    )
            elif debug:
                print(
                    "[parseContent] Skipping iframe without a data-src attribute."
                )

        content = "\n\n".join(content_parts)

        all_content.append(
            f"{challenge_title}\n"
            f"{'-' * len(challenge_title)}\n"
            f"{content}"
        )

        if debug:
            print(
                f"[parseContent] Finished processing challenge {i} "
                f"({len(content)} characters extracted)."
            )

    # Storing the combined content directly in pwnTree.
    moduleData["contents"]["content"] = "\n\n\n".join(all_content)

    if debug:
        print("[parseContent] Finished processing all challenges.")
        print("-" * 55)
    
def createOutputFileStructure(
    pwnTree: dict,
    output_dir: str = "pwn_scraped_output",
    debug: bool = True
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for dojo_name, dojo_data in pwnTree.items():
        safe_dojo_name = re.sub(r'[<>:"/\\|?*]', "_", dojo_name)
        dojo_path = output_path / safe_dojo_name
        dojo_path.mkdir(parents=True, exist_ok=True)

        for module_name, module_data in dojo_data["modules"].items():
            safe_module_name = re.sub(r'[<>:"/\\|?*]', "_", module_name)
            module_path = dojo_path / safe_module_name
            module_path.mkdir(parents=True, exist_ok=True)

            content = module_data["contents"].get("content", "")

            content_file = module_path / "content.txt"
            content_file.write_text(content, encoding="utf-8")

            if debug:
                print(f"[createOutputFileStructure] Saved: {content_file}")

    if debug:
        print("[createOutputFileStructure] Finished creating output files.")



def master(
    createJson: bool = True,
    checkInTerminal: bool = True,
    debug: bool = True,
    parseHrefsAgain: bool = True,
    parseContentAgain: bool = True,
    indicesToParse: set[str] | None = None,
    previewContentLength: int | None = None
):
    pwnTree = {}
    driverStarted = False

    if debug:
        print("=" * 60)
        print("[master] Starting scraper workflow.")
        print(f"[master] Debug enabled: {debug}")
        print(f"[master] Terminal output enabled: {checkInTerminal}")
        print(f"[master] JSON output enabled: {createJson}")
        print(f"[master] Re-scrape hrefs: {parseHrefsAgain}")
        print(f"[master] Re-scrape content: {parseContentAgain}")
        print("=" * 60)

    if not parseHrefsAgain:
        try:
            with open("Check/pwnTree.json", "r", encoding="utf-8") as file:
                pwnTree = json.load(file)

            if debug:
                print("[master] Successfully loaded pwnTree.json.")

        except FileNotFoundError:
            if debug:
                print("[master] JSON file not found; scraping URLs instead.")

            parseHrefsAgain = True

    if parseHrefsAgain:
        if debug:
            print("[master] Starting browser and scraping Dojos...")

        start("https://pwn.college/dojos", debug)
        driverStarted = True

        pwnTree = searchDojos(debug)

        if checkInTerminal:
            print("[master] Extracted Dojos:")
            pprint(pwnTree)
            print("-" * 55)

        if debug:
            print("[master] Parsing modules...")

        pwnTree = parseModules(pwnTree, debug)

        if checkInTerminal:
            print("[master] Resulting pwnTree:")
            pprint(pwnTree)
            print("-" * 55)

    if debug:
        print("[master] Validating requested module indices...")

    selectedIndices = validParsingIndices(
        pwnTree,
        debug=debug,
        indicesToParse=indicesToParse
    )

    moduleLookup = buildModuleLookup(
        pwnTree,
        debug=debug,
        checkInTerminal=checkInTerminal
    )

    selectedModules = {
        index: moduleLookup[index]
        for index in selectedIndices
        if index in moduleLookup
    }

    if checkInTerminal:
        print("[master] Selected modules:")
        pprint({
            index: moduleData["href"]
            for index, moduleData in selectedModules.items()
        })
        print("-" * 55)

    modulesToParse = {}

    for index, moduleData in selectedModules.items():
        contents = moduleData.get("contents", {})
        contentExists = bool(contents.get("content"))

        # this always executes for parseContentAgain = True, so every module that we selected gets parsed again,
        # however, if we aren't parsing again, it is only true for modules where content don't exist, which we store in modulesToParse
        # and parse again
        if parseContentAgain or not contentExists:
            modulesToParse[index] = moduleData

    if debug:
        print(
            f"[master] Modules selected: {len(selectedModules)}"
        )
        print(
            f"[master] Modules requiring content scraping: {len(modulesToParse)}"
        )

    for index, moduleData in modulesToParse.items():
        if debug:
            print(f"[master] Parsing content for module {index}...")

        parseContent(
            moduleData["href"],
            moduleData,
            debug=debug
        )

        if debug:
            print(f"[master] Content stored for module {index}.")

        if previewContentLength is not None:
            content = moduleData.get("contents", {}).get("content", "")

            print(f"\n[{index}] {len(content)} characters total:")
            print(content[:previewContentLength])
            print("\n")


    if createJson:
        os.makedirs("Check", exist_ok=True)

        if debug:
            print("[master] Saving pwnTree.json...")

        with open("Check/pwnTree.json", "w", encoding="utf-8") as file:
            json.dump(pwnTree, file, indent=4, ensure_ascii=False)

        if debug:
            print("[master] JSON saved successfully.")

    if driverStarted:
        if debug:
            print("[master] Waiting 2 seconds before closing browser...")

        time.sleep(2)

        # Uncomment input() if you want to keep the browser window open.
        # input()

        end(debug)

    if debug:
        print("[master] Workflow finished.")
        print("=" * 60)

    return pwnTree


pwnTree = master(
    createJson=True,
    checkInTerminal=True,
    debug=True,
    parseHrefsAgain=False,
    parseContentAgain=True,
    # indicesToParse,
    previewContentLength=500
)