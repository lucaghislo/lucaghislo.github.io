# lucaghislotti.com

Personal academic website of Luca Ghislotti, built with Jekyll on the [al-folio](https://github.com/alshedivat/al-folio) theme and deployed to GitHub Pages by `.github/workflows/deploy.yml` on every push to `master`.

## Common updates

| What | Where |
| --- | --- |
| Bio, photo, subtitle | `_pages/about.md` (photo in `assets/img/luca_pic.jpg`) |
| CV | replace `assets/pdf/CV_scientific_luca_ghislotti.pdf` |
| Publications | `_bibliography/papers.bib` |
| Publication thumbnails | `assets/img/publication_preview/` |
| Social links, SEO description, site options | `_config.yml` |

### Add a publication

```bash
python tools/add_paper.py 10.1109/TNS.2026.3700799 --preview first_page.pdf
```

Downloads the BibTeX from doi.org, normalizes it, creates the thumbnail (from an image or the first page of a PDF, needs `pip install pymupdf`) and appends the entry to `papers.bib`. Options: `--selected` shows it on the home page, `--dry-run` prints without writing, `--key` sets the citation key.

Optional fields you can add by hand: `pdf`, `arxiv`, `inspirehep_id`, `abstract`.

### Check the bibliography

```bash
python tools/check_bib.py
```

Reports missing thumbnails, duplicate keys/DOIs and missing fields. The deploy workflow runs it too and stops on errors.

## Notes

- Images in `assets/img/` are converted to responsive WebP at build time (ImageMagick in the workflow). Keep source images reasonably sized (max ~1200 px).
- Broken internal links are checked monthly by `.github/workflows/broken-links-site.yml` (also runnable by hand from the Actions tab).
- Local preview: `bundle install && bundle exec jekyll serve`, see [INSTALL.md](INSTALL.md).
