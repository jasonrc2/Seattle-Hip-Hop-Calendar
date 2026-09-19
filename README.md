# Seattle Hip-Hop Calendar

A deployable Seattle-area hip-hop community calendar focused on breaking, DJing, turntablism, cyphers, battles, beatmaking, graffiti, workshops, and live hip-hop.

## Current version

This starter is intentionally simple:
- responsive calendar UI
- category filters
- upcoming-event list
- source attribution
- JSON event data
- GitHub Actions scheduled refresh placeholder

## Make it genuinely live

The production architecture I recommend is:

1. `events.json` is the public event feed.
2. A scheduled job runs daily.
3. The collector checks approved public sources (206 Zulu, HeadSpin, Massive Monkees, venue calendars, Eventbrite/public event pages, etc.).
4. It normalizes dates/categories and deduplicates events.
5. It updates `public/events.json`.
6. Vercel/Netlify serves the site automatically.

### Deployment

Upload this folder to a GitHub repository, then import the repository into Vercel or Netlify.

No build step is required for the static site.

### Important

The included `refresh-events.yml` is a safe starter workflow and does not scrape sites yet. The next step is connecting the collector to specific public sources and handling each site's terms/rate limits.

For a production version, keep source URLs on every event and avoid treating an event as verified unless the source currently supports it.
