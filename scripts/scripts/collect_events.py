import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "public" / "events.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; SeattleHipHopCalendar/1.0; "
        "+https://github.com/jasonrc2/Seattle-Hip-Hop-Calendar)"
    )
}

TODAY = datetime.now().date()
END_DATE = TODAY + timedelta(days=120)


def fetch(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as exc:
        print(f"Could not fetch {url}: {exc}")
        return ""


def make_id(title, date, venue):
    raw = f"{title}-{date}-{venue}".lower()
    return re.sub(r"[^a-z0-9]+", "-", raw).strip("-")


def add_event(events, title, date, time, venue, category,
              source, url, description="", age="", price=""):
    if date < TODAY or date > END_DATE:
        return

    event = {
        "id": make_id(title, date.isoformat(), venue),
        "date": date.isoformat(),
        "title": title,
        "venue": venue,
        "city": "Seattle",
        "category": category,
        "time": time,
        "age": age,
        "price": price,
        "description": description,
        "source": source,
        "url": url,
        "last_verified_at": datetime.utcnow().isoformat() + "Z",
    }

    events[event["id"]] = event


def next_weekday(start, weekday):
    """
    Python weekday:
    Monday = 0
    Tuesday = 1
    ...
    Sunday = 6
    """
    days_ahead = (weekday - start.weekday()) % 7
    return start + timedelta(days=days_ahead)


# ------------------------------------------------------------
# 206 ZULU
# ------------------------------------------------------------

def collect_206_zulu(events):

    programs_url = "https://www.206zulu.org/programs/"
    venue_url = "https://www.206zulu.org/venue/washington-hall/"
    home_url = "https://www.206zulu.org/"

    # Soulful Mondays
    date = next_weekday(TODAY, 0)

    while date <= END_DATE:
        add_event(
            events,
            title="Soulful Mondays",
            date=date,
            time="6:00 PM – 9:00 PM",
            venue="Washington Hall",
            category="Dance / Cypher",
            source="206 Zulu",
            url=venue_url,
            description=(
                "Free, all-ages, all-styles weekly Hip-Hop gathering "
                "at Washington Hall."
            ),
            age="All Ages",
            price="Free",
        )
        date += timedelta(days=7)

    # The Beat Cypher — first Monday of each month
    year = TODAY.year
    month = TODAY.month

    for _ in range(6):
        first = datetime(year, month, 1).date()
        beat_cypher_date = next_weekday(first, 0)

        # If first Monday is before today, it won't be added.
        add_event(
            events,
            title="The Beat Cypher",
            date=beat_cypher_date,
            time="6:00 PM – 9:00 PM",
            venue="Washington Hall",
            category="Production",
            source="206 Zulu",
            url="https://www.206zulu.org/programs/the-beat-cypher/",
            description=(
                "Beatmaking session followed by a beat cypher. "
                "Bring your gear and share your work."
            ),
            age="16+",
            price="Free",
        )

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

    # Try to collect actual upcoming Washington Hall events
    html = fetch(venue_url)

    if html:
        soup = BeautifulSoup(html, "html.parser")

        # Look for obvious event titles and dates from the page.
        for article in soup.find_all(["article", "div"], limit=500):

            text = " ".join(article.stripped_strings)

            if not text:
                continue

            # Detect common date format such as:
            # September 21 @ 6:00 PM - 9:00 PM
            match = re.search(
                r"("
                r"January|February|March|April|May|June|July|August|"
                r"September|October|November|December"
                r")\s+(\d{1,2})",
                text,
                re.IGNORECASE,
            )

            if not match:
                continue

            month_name = match.group(1)
            day = int(match.group(2))

            try:
                month_number = datetime.strptime(
                    month_name[:3], "%b"
                ).month
            except ValueError:
                continue

            event_date = datetime(TODAY.year, month_number, day).date()

            # Handle events crossing into next year.
            if event_date < TODAY - timedelta(days=30):
                event_date = datetime(
                    TODAY.year + 1, month_number, day
                ).date()

            if not (TODAY <= event_date <= END_DATE):
                continue

            # Skip recurring events we've already added.
            title = ""

            heading = article.find(
                ["h1", "h2", "h3", "h4", "h5", "h6"]
            )

            if heading:
                title = heading.get_text(" ", strip=True)

            if not title:
                continue

            # Only import likely relevant Hip-Hop/community events.
            keywords = [
                "hip hop",
                "hip-hop",
                "zulu",
                "cypher",
                "beat",
                "dj",
                "dance",
                "breaking",
                "battle",
                "graffiti",
                "soulful",
                "questlove",
                "rap",
            ]

            if not any(k in text.lower() for k in keywords):
                continue

            add_event(
                events,
                title=title,
                date=event_date,
                time="",
                venue="Washington Hall",
                category="Music / Hip-Hop",
                source="206 Zulu",
                url=venue_url,
                description=text[:500],
            )


# ------------------------------------------------------------
# HEADSPIN PRODUCTIONS
# ------------------------------------------------------------

def collect_headspin(events):

    url = "https://headspinproductions.org/events"

    # Thursday open practice
    date = next_weekday(TODAY, 3)

    while date <= END_DATE:
        add_event(
            events,
            title="HeadSpin Thursday Open Practice",
            date=date,
            time="6:30 PM – 10:00 PM",
            venue="The Studio at 2+U",
            category="Dance / Cypher",
            source="HeadSpin Productions",
            url=url,
            description=(
                "Weekly open practice session. "
                "All ages and free to attend."
            ),
            age="All Ages",
            price="Free",
        )
        date += timedelta(days=7)

    # Monthly second-Saturday 1-on-1 All Styles Battle
    current = TODAY

    while current <= END_DATE:

        first_day = current.replace(day=1)

        second_saturday = (
            first_day
            + timedelta(
                days=(5 - first_day.weekday()) % 7
            )
            + timedelta(days=7)
        )

        if second_saturday >= TODAY:
            add_event(
                events,
                title="HeadSpin 1-on-1 All Styles Dance Battle",
                date=second_saturday,
                time="8:00 PM – 12:00 AM",
                venue="The Octopus Bar",
                category="Battles",
                source="HeadSpin Productions",
                url=url,
                description=(
                    "Monthly 1-on-1 all-styles dance battle."
                ),
                age="21+",
            )

        if current.month == 12:
            current = current.replace(
                year=current.year + 1,
                month=1,
                day=1,
            )
        else:
            current = current.replace(
                month=current.month + 1,
                day=1,
            )


# ------------------------------------------------------------
# MASSIVE MONKEES / THE BEACON
# ------------------------------------------------------------

def collect_beacon(events):

    url = "https://www.massivemonkees.com/the-beacon-studio"

    # Soul City — every Wednesday
    date = next_weekday(TODAY, 2)

    while date <= END_DATE:
        add_event(
            events,
            title="Soul City",
            date=date,
            time="8:45 PM – 10:45 PM",
            venue="The Beacon",
            category="Dance / Cypher",
            source="Massive Monkees / The Beacon",
            url=url,
            description=(
                "Weekly House session hosted by Orb. "
                "Open community dance session, often with a live DJ."
            ),
            price="$7",
        )
        date += timedelta(days=7)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    events = {}

    collect_206_zulu(events)
    collect_headspin(events)
    collect_beacon(events)

    output = sorted(
        events.values(),
        key=lambda event: (
            event["date"],
            event["time"],
            event["title"].lower(),
        ),
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(output)} events to {OUTPUT}")


if __name__ == "__main__":
    main()
