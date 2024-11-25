# Web Snatcher

A cheeky little tool for turning web pages into PDFs.
I use it for a specific news outlet (the42.ie) with HTML-heavy pages.
This tool will probably work poorly for JS heavy sites or those which enforce paywalls properly at the API-level.

## Why?

Some news sites can be a bit... restrictive and sometimes their paywalls are not enforced at the API level :p.
Or maybe because sometimes you just want to read an article without all the extra jazz.

## How it works

1. You give it a URL
2. It fetches the page
3. It turns it into a PDF
4. You get to read your article

## Installation

1. Clone this repo
2. Install the dependencies (we use Poetry, so `poetry install` should do the trick)
3. install wkhtmltopdf

## Usage

Run it with `poetry run python -m web_snatcher.main <url>`
