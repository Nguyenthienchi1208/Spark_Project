"""Enrich events with domain-country, browser, and OS for fact reporting."""

from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructType, StructField

# Country from Glamira storefront domain (TLD), not IP GeoIP
DOMAIN_COUNTRY = {
    "fr": "France",
    "de": "Germany",
    "nl": "Netherlands",
    "be": "Belgium",
    "es": "Spain",
    "it": "Italy",
    "at": "Austria",
    "ch": "Switzerland",
    "uk": "United Kingdom",
    "co.uk": "United Kingdom",
    "com": "International",
    "se": "Sweden",
    "dk": "Denmark",
    "fi": "Finland",
    "pl": "Poland",
    "cz": "Czech Republic",
    "hu": "Hungary",
    "ro": "Romania",
    "pt": "Portugal",
    "ie": "Ireland",
    "gr": "Greece",
    "bg": "Bulgaria",
    "sk": "Slovakia",
    "si": "Slovenia",
    "hr": "Croatia",
    "lt": "Lithuania",
    "lv": "Latvia",
    "ee": "Estonia",
    "lu": "Luxembourg",
    "ca": "Canada",
    "au": "Australia",
    "nz": "New Zealand",
    "za": "South Africa",
    "in": "India",
    "ae": "United Arab Emirates",
    "sa": "Saudi Arabia",
    "mx": "Mexico",
    "br": "Brazil",
    "tr": "Turkey",
    "ru": "Russia",
    "ua": "Ukraine",
    "no": "Norway",
}

_UA_SCHEMA = StructType([
    StructField("browser", StringType(), True),
    StructField("os", StringType(), True),
])

_DOMAIN_SCHEMA = StructType([
    StructField("domain", StringType(), True),
    StructField("country_domain", StringType(), True),
])


def _parse_ua(user_agent: str):
    if not user_agent:
        return ("Unknown", "Unknown")
    try:
        from user_agents import parse

        ua = parse(user_agent)
        return (ua.browser.family or "Unknown", ua.os.family or "Unknown")
    except Exception:
        return ("Unknown", "Unknown")


def _domain_country(host: str):
    if not host:
        return (None, "Unknown")
    host = host.lower().strip(".")
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(".co.uk"):
        return (host, DOMAIN_COUNTRY["co.uk"])
    parts = host.split(".")
    if len(parts) < 2:
        return (host, "Unknown")
    tld = parts[-1]
    return (host, DOMAIN_COUNTRY.get(tld, tld.upper()))


def enrich_event_attrs(df):
    """Add domain, country_domain, browser, os from current_url / user_agent."""
    parse_ua_udf = F.udf(_parse_ua, _UA_SCHEMA)
    domain_udf = F.udf(_domain_country, _DOMAIN_SCHEMA)

    out = df
    if "current_url" not in out.columns:
        out = out.withColumn("current_url", F.lit(None).cast(StringType()))
    if "referrer_url" not in out.columns:
        out = out.withColumn("referrer_url", F.lit(None).cast(StringType()))
    if "user_agent" not in out.columns:
        out = out.withColumn("user_agent", F.lit(None).cast(StringType()))

    host = F.regexp_extract(F.col("current_url"), r"https?://([^/]+)", 1)
    out = out.withColumn("_host", F.when(F.length(host) > 0, host).otherwise(F.lit(None)))
    out = out.withColumn("_dom", domain_udf(F.col("_host")))
    out = out.withColumn("domain", F.col("_dom.domain"))
    out = out.withColumn("country_domain", F.coalesce(F.col("_dom.country_domain"), F.lit("Unknown")))

    out = out.withColumn("_ua", parse_ua_udf(F.col("user_agent")))
    out = out.withColumn("browser", F.coalesce(F.col("_ua.browser"), F.lit("Unknown")))
    out = out.withColumn("os", F.coalesce(F.col("_ua.os"), F.lit("Unknown")))

    return out.drop("_host", "_dom", "_ua")
