
-- 1. Count of Movies vs TV Shows
SELECT type, COUNT(*) AS total
FROM netflix_titles
GROUP BY type
ORDER BY total DESC;

-- 2. Top 10 countries by content production
SELECT country, COUNT(*) AS total
FROM netflix_titles
GROUP BY country
ORDER BY total DESC
LIMIT 10;

-- 3. Number of titles added per year
SELECT year_added, COUNT(*) AS total
FROM netflix_titles
WHERE year_added IS NOT NULL
GROUP BY year_added
ORDER BY year_added;

-- 4. Content distribution by rating
SELECT rating, COUNT(*) AS total
FROM netflix_titles
GROUP BY rating
ORDER BY total DESC;

-- 5. Top 10 directors by number of titles
SELECT director, COUNT(*) AS total
FROM netflix_titles
WHERE director != 'Unknown'
GROUP BY director
ORDER BY total DESC
LIMIT 10;

-- 6. Country ranking by content count using RANK
SELECT country,
       COUNT(*) AS total,
       RANK() OVER (ORDER BY COUNT(*) DESC) AS country_rank
FROM netflix_titles
GROUP BY country
ORDER BY country_rank
LIMIT 10;

-- 7. Most common content type per year using ROW_NUMBER
WITH ranked AS (
    SELECT year_added,
           type,
           COUNT(*) AS total,
           ROW_NUMBER() OVER (PARTITION BY year_added ORDER BY COUNT(*) DESC) AS rn
    FROM netflix_titles
    WHERE year_added IS NOT NULL
    GROUP BY year_added, type
)
SELECT year_added, type, total
FROM ranked
WHERE rn = 1
ORDER BY year_added;

-- 8. Movies vs TV Shows ratio per year
SELECT year_added,
       COUNT(*) FILTER (WHERE type = 'Movie') AS movies,
       COUNT(*) FILTER (WHERE type = 'TV Show') AS tv_shows,
       ROUND(COUNT(*) FILTER (WHERE type = 'Movie') * 100.0 / COUNT(*), 1) AS movie_pct
FROM netflix_titles
WHERE year_added IS NOT NULL
GROUP BY year_added
ORDER BY year_added;

-- 9. Classify movies by duration using CASE WHEN
SELECT title,
       duration,
       CASE
           WHEN CAST(SPLIT_PART(duration, ' ', 1) AS INT) < 60  THEN 'Short (< 60 min)'
           WHEN CAST(SPLIT_PART(duration, ' ', 1) AS INT) < 120 THEN 'Medium (60-120 min)'
           ELSE 'Long (> 120 min)'
       END AS duration_category
FROM netflix_titles
WHERE type = 'Movie'
ORDER BY duration DESC
LIMIT 20;

--10 Top 5 titles per country using ROW_NUMBER in CTE
WITH country_ranked AS (
    SELECT country,
           title,
           type,
           release_year,
           ROW_NUMBER() OVER (PARTITION BY country ORDER BY release_year DESC) AS rn
    FROM netflix_titles
    WHERE country != 'Unknown'
)
SELECT country, title, type, release_year, rn
FROM country_ranked
WHERE rn <= 5
ORDER BY country, rn;



