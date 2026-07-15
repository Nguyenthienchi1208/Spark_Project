-- Non-destructive migration for existing warehouse
ALTER TABLE fact_product_view ADD COLUMN IF NOT EXISTS referrer_url TEXT;
ALTER TABLE fact_product_view ADD COLUMN IF NOT EXISTS current_url TEXT;
ALTER TABLE fact_product_view ADD COLUMN IF NOT EXISTS domain VARCHAR(255);
ALTER TABLE fact_product_view ADD COLUMN IF NOT EXISTS country_domain VARCHAR(100);
ALTER TABLE fact_product_view ADD COLUMN IF NOT EXISTS browser VARCHAR(100);
ALTER TABLE fact_product_view ADD COLUMN IF NOT EXISTS os VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_fact_country_domain ON fact_product_view (country_domain);
CREATE INDEX IF NOT EXISTS idx_fact_browser_os ON fact_product_view (browser, os);
