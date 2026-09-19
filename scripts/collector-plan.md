Live event collector plan
The collector should run daily and use public, permitted event pages.
Source tiers
First-party community sources:
206 Zulu programs and productions
HeadSpin Productions events
Massive Monkees / Beacon Studio
First-party venue calendars:
Washington Hall
The Octopus Bar
Nectar Lounge
Neptune Theatre
Paramount Theatre
WAMU Theater
The Crocodile / Showbox venues
Public event aggregators:
Eventbrite
Songkick
Ticketmaster
Normalization
Every event should become:
id, date, end_date, time, title, venue, city, category, age, price,
description, source, url, last_verified_at
Rules
Prefer first-party sources when dates conflict.
Never invent missing times.
Preserve source URLs.
Deduplicate by normalized title + date + venue.
Keep cancelled/postponed events marked rather than silently deleting them.
Rate-limit requests and respect robots.txt and site terms.
Use a human-review queue for ambiguous events.
