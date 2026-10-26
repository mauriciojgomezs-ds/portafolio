"""Validate every local page and asset link in the generated site."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json

OUT = Path(__file__).resolve().parents[1] / 'dist'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])


def check():
    errors = []
    pages = {}
    count = 0
    for file in OUT.rglob('*.html'):
        page = Links()
        page.feed(file.read_text(encoding='utf-8'))
        pages[file.resolve()] = page
    for file, page in pages.items():
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                if parsed.scheme and parsed.scheme not in {'http', 'https', 'mailto'}:
                    errors.append(f'{file}: unsafe scheme {link}')
                continue
            count += 1
            if parsed.path.startswith('/'):
                errors.append(f'{file}: absolute path incompatible with repository Pages: {link}')
                continue
            target = (file.parent / unquote(parsed.path)).resolve() if parsed.path else file
            if target.is_dir():
                target /= 'index.html'
            if not target.is_relative_to(OUT.resolve()) or not target.exists():
                errors.append(f'{file.relative_to(OUT)}: missing {link}')
            elif parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                errors.append(f'{file.relative_to(OUT)}: missing heading {link}')
    # Datasets, environments and project execution artifacts must never be published.
    excluded = {'raw', 'processed', 'back', 'models', '.venv', '.git', 'runs'}
    for file in OUT.rglob('*'):
        if any(p in excluded or p.startswith('.env') for p in file.relative_to(OUT).parts):
            errors.append(f'Forbidden published path: {file}')
    result = {'html_pages': len(pages), 'local_links_checked': count, 'errors': errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)
    return result


if __name__ == '__main__':
    check()
