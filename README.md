# pwn.college Scraper

A Python scraper for collecting and organizing the dojo, module, and challenge content available on [pwn.college](https://pwn.college/dojos).

The scraper builds a structured representation of the dojo and module hierarchy, stores it in JSON, and saves module content into individual text files organized by dojo.

This project is intended for personal educational use and research. It is unofficial and is not affiliated with or endorsed by pwn.college.

**Last verified working:** October 27, 2026

## Features

- Discovers dojo and module links using Selenium.
- Retrieves and parses module content using `requests` and BeautifulSoup.
- Organizes dojos, modules, and their content into a nested Python dictionary.
- Saves the discovered structure in a JSON file for reuse.
- Saves module content in individual `.txt` files, organized into dojo folders.
- Supports selecting specific dojos or modules using their indices.
- Allows previously saved content to be reused or reparsed.
- Provides configurable request delays to reduce unnecessary pressure on the website.
- Includes debugging output and optional terminal previews.

## Requirements

- Python
- [uv](https://docs.astral.sh/uv/) for dependency management
- Google Chrome
- Selenium-compatible ChromeDriver setup
- The Python packages used by the project, including Selenium, Requests, and BeautifulSoup

The project uses Python's built-in `json` module. It does not need to be installed separately.

## Installation

Clone or download the repository, then open a terminal in the project directory.

If the project already contains a `pyproject.toml` and `uv.lock`, install its dependencies with:

```bash
uv sync
```

Otherwise, initialize the project and install the required packages as appropriate for your existing setup.

Run the scraper using the Python entry-point file that contains `master()`.

For example, if your main script is named `main.py`:

```bash
uv run main.py
```

Replace `main.py` with the actual filename if it differs.

## Output Structure

The scraper maintains two kinds of data:

1. A JSON file containing the discovered dojo/module hierarchy and scraped content.
2. Text files containing the content of individual modules.

The default JSON cache path is:

```text
Check/
└── pwnTree.json
```

The scraped text files are organized under:

```text
pwn_scraped_output/
└── <dojo folder>/
    ├── <module title>.txt
    ├── <module title>.txt
    └── ...
```

Each dojo has its own folder, and each module is stored in a separate text file within the corresponding dojo folder.

The JSON file is intended to preserve the structure and scraped data between runs, while the text files provide a convenient way to browse the collected content without opening the JSON file.

## How `master()` Works

`master()` is the main function that coordinates the scraping process. Rather than requiring you to call each helper function manually, it controls the discovery, caching, parsing, previewing, and output stages.

Its parameters allow you to choose which stages to run and which content to parse.

The current interface is:

```python
master(
    createJson=True,
    checkInTerminal=True,
    debug=True,
    parseHrefsAgain=True,
    parseContentAgain=True,
    indicesToParse=None,
    previewContentLength=None,
    rateLimit=1.0,
)
```

### Parameters

| Parameter | Description |
|---|---|
| `createJson` | Controls whether the updated `pwnTree` is saved to the JSON cache. |
| `checkInTerminal` | Controls whether scraped content is displayed in the terminal. |
| `debug` | Enables additional diagnostic and progress messages. |
| `parseHrefsAgain` | Controls whether the dojo/module hierarchy is discovered again or loaded from the existing JSON cache. |
| `parseContentAgain` | Controls whether existing module content is scraped again. When disabled, already available content can be reused, while missing content may still need to be collected. |
| `indicesToParse` | A set of dojo or module indices specifying which modules to parse. Use `None` to select all available modules. |
| `previewContentLength` | Limits the length of content displayed in the terminal preview. `None` leaves the preview untruncated by this setting. |
| `rateLimit` | Minimum interval, in seconds, between the starts of requests managed by the scraper. |

### Example: Normal Run

```python
master()
```

This uses the default settings to discover the hierarchy, collect module content, display the configured terminal output, and save the JSON cache.

### Example: Reuse the Existing Hierarchy

```python
master(
    parseHrefsAgain=False,
)
```

This avoids rediscovering the dojo/module links and instead uses the existing JSON cache.

Use this when the saved hierarchy is still suitable and you only need to work with its content.

The cache must exist and contain valid JSON. If it does not, the scraper cannot load the saved hierarchy.

### Example: Reparse Module Content

```python
master(
    parseHrefsAgain=False,
    parseContentAgain=True,
)
```

This reuses the saved hierarchy while requesting module content again.

### Example: Disable Terminal Output and Debug Messages

```python
master(
    checkInTerminal=False,
    debug=False,
)
```

This reduces console output. It does not disable scraping or file generation.

### Example: Limit the Preview

```python
master(
    previewContentLength=500,
)
```

This limits the displayed preview to the configured length. It does not mean that only that much content is scraped or saved.

## JSON Structure

The JSON cache represents the hierarchy of dojos and modules using nested dictionaries.

Conceptually, the structure looks like this:

```json
{
  "Example Dojo": {
    "dojoIndex": "1",
    "href": "https://pwn.college/example-dojo",
    "modules": {
      "Example Module": {
        "moduleIndex": "1.1",
        "href": "https://pwn.college/example-module",
        "contents": {
          "content": "Scraped module content goes here"
        }
      }
    }
  }
}
```

The names and URLs in this example are illustrative.

### Dojo Fields

Each dojo entry contains:

- `dojoIndex`: the index assigned to the dojo.
- `href`: the URL of the dojo.
- `modules`: a dictionary containing the dojo's modules.

The dojo's title is used as the dictionary key.

### Module Fields

Each module entry contains:

- `moduleIndex`: the index assigned to the module.
- `href`: the URL of the module.
- `contents`: a dictionary containing the scraped content and any other content-related data maintained by the scraper.

The module's title is used as the dictionary key.

### Why Use a Nested Dictionary?

This representation makes it possible to:

- Retrieve a dojo and its modules by title.
- Find the URL associated with a dojo or module.
- Select modules by their indices.
- Store scraped content alongside the module it belongs to.
- Save and reload the entire hierarchy using JSON.

The indices are stored as strings so that they can be used consistently for selection and lookup.

## Selecting Content with `indicesToParse`

The `indicesToParse` parameter determines which modules are selected for content parsing.

It accepts a set of strings representing dojo indices, module indices, or a combination of both.

### Index Format

Dojo indices identify individual dojos, while module indices identify modules within the overall hierarchy.

For example:

```text
1       -> Dojo 1
1.1     -> Module 1.1
1.2     -> Module 1.2
2       -> Dojo 2
2.1     -> Module 2.1
```

The exact indices available depend on the hierarchy discovered by the scraper.

### Parse Every Module

```python
master(
    indicesToParse=None,
)
```

Passing `None` selects all available modules.

### Parse One Dojo

```python
master(
    indicesToParse={"1"},
)
```

This selects the modules belonging to dojo `1`.

The dojo index is expanded into the corresponding module indices by the selection logic.

### Parse One Module

```python
master(
    indicesToParse={"1.2"},
)
```

This selects module `1.2` without intentionally selecting every module in dojo `1`.

### Parse Multiple Modules

```python
master(
    indicesToParse={"1.2", "3.3"},
)
```

This selects modules `1.2` and `3.3`.

### Combine Dojo and Module Indices

```python
master(
    indicesToParse={"1", "3.3"},
)
```

This selects all modules in dojo `1` and module `3.3`.

### Important Notes

- Use strings, not integers, for the indices.
- Because the parameter is a set, duplicate values are automatically eliminated.
- Use the indices that actually exist in the current hierarchy.
- The selection determines which modules are parsed; it does not necessarily delete files belonging to unselected modules.
- If you want to reparse a single dojo, select that dojo's index rather than selecting every dojo.

## Rate Limiting

The `rateLimit` parameter controls how frequently the scraper starts requests that it manages.

For example:

```python
master(
    rateLimit=1.0,
)
```

This requests a minimum interval of approximately one second between managed request starts.

### Examples

| Value | Minimum interval | Approximate maximum start rate |
|---:|---:|---:|
| `0` | No added delay | Unrestricted by this delay |
| `0.5` | 0.5 seconds | 2 starts per second |
| `1.0` | 1 second | 1 start per second |
| `2.0` | 2 seconds | 1 start every 2 seconds |

These rates are theoretical limits on the requests managed by the scraper, not guarantees of overall traffic or completion time.

### What Is Rate-Limited?

The delay is applied before the scraper's managed Selenium page navigations and `requests.get()` calls.

The implementation uses a shared timestamp to calculate how much time has elapsed since the previous managed request start. If the configured interval has not elapsed, it waits for the remaining time.

### Limitations

- Selenium navigation can trigger additional requests for scripts, stylesheets, images, and other resources. The delay does not individually throttle those browser-generated requests.
- Rate limiting does not automatically retry failed requests or handle HTTP `429 Too Many Requests` responses.
- A longer delay may make the scraping process take considerably longer.
- A delay is not permission to ignore the website's rules or restrictions.

Use a conservative value, avoid unnecessary scraping, and stop if the website operator asks you to stop.

## Troubleshooting

### 1. WebDriver Fails

If Selenium cannot start Chrome or navigate to a page, check that Chrome is installed and that your Selenium/ChromeDriver setup is working.

### 2. Requests Raise an Error

If `requests.get()` fails, check your internet connection, the target URL, and the HTTP status or exception. The website may be temporarily unavailable or may restrict the request.

### 3. Elements Are Not Found

If Selenium or BeautifulSoup cannot find an expected element, the website's HTML structure may have changed, or the element may not be present in the returned page. Check the selector and inspect the page source.

### 4. YouTube Iframe Links

Some modules contain embedded YouTube videos. The scraper may encounter iframe URLs through attributes such as `data-src`. These URLs can differ from ordinary YouTube watch links.

An extracted embed URL does not guarantee that the video is available, accessible, or playable.

### 5. `JSONDecodeError`

This error usually means the JSON cache is empty, malformed, incomplete, or not valid JSON.

Check `Check/pwnTree.json`. If the cached hierarchy is no longer usable, regenerate it by running the scraper with `parseHrefsAgain=True`. If needed, remove the invalid cache before regenerating it.

### 6. New Content and Old Content

The JSON cache and the generated text files serve different purposes.

- `parseHrefsAgain` controls whether the hierarchy is discovered again.
- `parseContentAgain` controls whether existing module content is refreshed.
- `createJson` controls whether the JSON cache is written.

If you want to collect newly added content, refresh the relevant hierarchy and reparse the relevant modules. Existing cached content may otherwise remain unchanged when reparsing is disabled.

### 7. Old Files Remain After Scraping

The current solution is to **delete the affected dojo's output folder and reparse only that dojo** using `indicesToParse`.

For example, if dojo `3` has stale or obsolete module files, delete its corresponding folder inside `pwn_scraped_output/` and rerun the scraper with:

```python
master(
    indicesToParse={"3"},
    parseContentAgain=True,
)
```

This rebuilds the selected dojo's output from the modules processed by the scraper.

Be careful to delete only the intended dojo folder. This workaround is necessary because the current output process does not automatically remove every stale file that no longer corresponds to a module in the current hierarchy.

### 8. Scraping Stops Partway Through

If the scraper stops before completing, check the last error or progress message printed in the terminal.

Possible causes include network errors, website changes, browser failures, or a request being rejected. If appropriate, increase `rateLimit` and rerun only the affected dojo or modules using `indicesToParse`.

A rerun can reuse the saved hierarchy when `parseHrefsAgain=False`, provided that the JSON cache exists and is valid.

## Responsible Use

This project is an independent, unofficial tool for navigating and collecting publicly accessible educational content from pwn.college. It is not affiliated with, endorsed by, or sponsored by pwn.college.

By using this software, you are expected to use it responsibly and respect the website, its operators, and its educational purpose.

### 1. Respect the Website

- Use reasonable request delays and configure rate limits conservatively.
- Avoid excessive, unnecessary, or concurrent requests that could burden the website or its infrastructure.
- Respect the website's terms of service, applicable access restrictions, and instructions from its operators.
- Stop automated requests if asked to do so by the website's operators or if your activity appears to be causing disruption.
- Do not bypass authentication, access controls, rate limits, or other technical restrictions.

### 2. Respect Educational Integrity

- Do not use this software to facilitate cheating, unauthorized collaboration, or other violations of applicable course or institutional policies.
- Before collecting or publishing educational materials, check the rules applicable to the relevant course and content.
- Do not publicly redistribute challenge solutions, answer keys, or other restricted materials unless you have permission to do so.

### 3. Respect Third-Party Rights

This repository's software license applies only to the original code covered by that license. It does not grant permission to reproduce, publish, or redistribute content belonging to pwn.college or other third parties.

You are responsible for determining whether your collection, storage, modification, or redistribution of scraped material is permitted by applicable law, website terms, and the relevant rights holders.

### 4. No Guarantee of Permission

The fact that content is publicly accessible does not necessarily mean it may be collected or redistributed without restrictions. This project does not guarantee that any particular scraping activity is permitted by pwn.college.

## Takedown Requests

The author reserves the right to remove, disable access to, or stop distributing this repository at any time.

If the owner or an authorized representative of pwn.college requests that this project be taken down, the author intends to comply with the request promptly and discontinue public distribution of the repository to the extent reasonably practicable.

Users are respectfully asked not to redistribute copies of this repository or maintain mirrors for the purpose of circumventing such a takedown request.

This section expresses the author's commitment to respecting the website owner's requests. It does not imply that pwn.college owns this project's original code or that the website owner has a particular legal right to require its removal in every circumstance.

## License

This project is distributed under the MIT License. See the `LICENSE` file for the full license text.

The MIT License applies to the original code covered by the license. It does not grant rights to third-party website content collected by the scraper.

The responsible-use and takedown sections express the author's expectations and intentions. Under the MIT License, they do not automatically create additional enforceable restrictions on the permissions granted by that license.

## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied. The author makes no guarantee that it will operate without errors, remain compatible with pwn.college, or comply with the website's current policies.

Users are responsible for their own use of the software and for ensuring that their activities comply with applicable requirements.
