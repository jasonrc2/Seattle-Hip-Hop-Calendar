import json
import re
from datetime import datetime, timedelta
from pathlib import Path

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
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        return response.text
    except Exception as exc:
        print(f"Could not fetch {url}: {exc}")
        return ""


def make_id(title, date, venue):
    raw = f"{title}-{date}-{venue}".lower()
    return re.sub(r"[^a-z0-9]+", "-", raw).strip("-")


def add_event(
    events,
    title,
    date,
    time,
    venue,
    category,
    source,
    url,
    description="",
    age="",
    price="",
):
    if date < TODAY or date > END_DATE:
        return

    event = {
        "id": make_id(
            title,
            date.isoformat(),
            venue,
        ),
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
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6
    """

    days_ahead = (
        weekday - start.weekday()
    ) % 7

    return start + timedelta(
        days=days_ahead
    )


# ============================================================
# 206 ZULU
# ============================================================

def collect_206_zulu(events):

    programs_url = (
        "https://www.206zulu.org/programs/"
    )

    venue_url = (
        "https://www.206zulu.org/venue/"
        "washington-hall/"
    )

    # --------------------------------------------------------
    # Soulful Mondays
    # --------------------------------------------------------

    date = next_weekday(
        TODAY,
        0,
    )

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
                "Free, all-ages, all-styles "
                "weekly Hip-Hop gathering "
                "at Washington Hall."
            ),
            age="All Ages",
            price="Free",
        )

        date += timedelta(
            days=7
        )

    # --------------------------------------------------------
    # The Beat Cypher
    # First Monday of each month
    # --------------------------------------------------------

    year = TODAY.year
    month = TODAY.month

    for _ in range(6):

        first = datetime(
            year,
            month,
            1,
        ).date()

        beat_cypher_date = next_weekday(
            first,
            0,
        )

        add_event(
            events,
            title="The Beat Cypher",
            date=beat_cypher_date,
            time="6:00 PM – 9:00 PM",
            venue="Washington Hall",
            category="Production",
            source="206 Zulu",
            url=(
                "https://www.206zulu.org/"
                "programs/the-beat-cypher/"
            ),
            description=(
                "Beatmaking session followed "
                "by a beat cypher. Bring your "
                "gear and share your work."
            ),
            age="16+",
            price="Free",
        )

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1


# ============================================================
# HEADSPIN PRODUCTIONS
# ============================================================

def collect_headspin(events):

    url = (
        "https://headspinproductions.org/events"
    )

    # --------------------------------------------------------
    # Thursday Open Practice
    # --------------------------------------------------------

    date = next_weekday(
        TODAY,
        3,
    )

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
                "Weekly open practice session."
            ),
            age="All Ages",
            price="Free",
        )

        date += timedelta(
            days=7
        )

    # --------------------------------------------------------
    # Monthly 1-on-1 All Styles Battle
    # Second Saturday
    # --------------------------------------------------------

    current = TODAY.replace(
        day=1
    )

    while current <= END_DATE:

        first_day = current

        first_saturday_offset = (
            5 - first_day.weekday()
        ) % 7

        first_saturday = (
            first_day
            + timedelta(
                days=first_saturday_offset
            )
        )

        second_saturday = (
            first_saturday
            + timedelta(days=7)
        )

        add_event(
            events,
            title=(
                "HeadSpin 1-on-1 "
                "All Styles Dance Battle"
            ),
            date=second_saturday,
            time="8:00 PM – 12:00 AM",
            venue="The Octopus Bar",
            category="Battles",
            source="HeadSpin Productions",
            url=url,
            description=(
                "Monthly 1-on-1 all-styles "
                "dance battle."
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


# ============================================================
# MASSIVE MONKEES / THE BEACON
# ============================================================

def collect_beacon(events):

    url = (
        "https://www.massivemonkees.com/"
        "the-beacon-studio"
    )

    # --------------------------------------------------------
    # Soul City
    # Every Wednesday
    # --------------------------------------------------------

    date = next_weekday(
        TODAY,
        2,
    )

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
                "Weekly House session hosted "
                "by Orb. Open community dance "
                "session, often with a live DJ."
            ),
            price="$7",
        )

        date += timedelta(
            days=7
        )


# ============================================================
# MAIN
# ============================================================

def main():

    events = {}

    print("Collecting 206 Zulu events...")
    collect_206_zulu(events)

    print("Collecting HeadSpin events...")
    collect_headspin(events)

    print("Collecting Beacon events...")
    collect_beacon(events)

    output = sorted(
        events.values(),
        key=lambda event: (
            event["date"],
            event["time"],
            event["title"].lower(),
        ),
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Wrote {len(output)} events "
        f"to {OUTPUT}"
    )


if __name__ == "__main__":
    main()
